"""akshare 数据源封装（主数据源）"""
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from datetime import datetime
from typing import Optional

import pandas as pd
import loguru

logger = loguru.logger

PRICE_COLUMN_MAP = {
    '日期': 'date', '股票代码': 'code', '开盘': 'open', '收盘': 'close',
    '最高': 'high', '最低': 'low', '成交量': 'volume', '成交额': 'amount',
    '振幅': 'amplitude', '涨跌幅': 'pct_change', '涨跌额': 'change', '换手率': 'turnover',
}


def fetch_price(code: str, start_date: str, end_date: str, timeout: int = 10) -> Optional[pd.DataFrame]:
    """获取单只股票历史行情（前复权），超时视为失败以便上层走兜底数据源"""
    import akshare as ak

    if not (code.endswith(".SH") or code.endswith(".SZ")):
        return None
    stock_code = code.split(".")[0]

    def fetch():
        return ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date, adjust="qfq")

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fetch)
        try:
            df = future.result(timeout=timeout)
        except FutureTimeoutError:
            logger.error(f"akshare 获取 {code} 数据超时（{timeout}秒）")
            return None

    if df is None or df.empty:
        return None

    df = df.rename(columns=PRICE_COLUMN_MAP)
    df['date'] = pd.to_datetime(df['date'])
    df['code'] = code
    return df.sort_values('date')


def fetch_spot_map() -> dict:
    """获取全市场实时行情快照，用于提取 PE/PB/市值"""
    import akshare as ak

    spot_df = ak.stock_zh_a_spot_em()
    spot_data = {}
    for _, row in spot_df.iterrows():
        spot_data[row['代码']] = {
            'pe': row.get('市盈率-动态'),
            'pb': row.get('市净率'),
            'market_cap': row.get('总市值'),
        }
    return spot_data


def fetch_financial(code: str, spot_data: dict) -> dict:
    """获取财务指标"""
    import akshare as ak

    stock_code = code.split(".")[0]
    pe = pb = market_cap = None
    if spot_data and stock_code in spot_data:
        pe = spot_data[stock_code].get('pe')
        pb = spot_data[stock_code].get('pb')
        market_cap = spot_data[stock_code].get('market_cap')

    roe = rev_growth = net_profit = revenue = None
    finance_df = ak.stock_financial_analysis_indicator(symbol=stock_code)
    if not finance_df.empty:
        latest = finance_df.iloc[0]
        roe = latest.get('净资产收益率(%)')
        rev_growth = latest.get('营业收入同比增长率(%)')
        net_profit = latest.get('净利润(元)')
        revenue = latest.get('营业收入(元)')

    return {
        'code': code,
        'revenue': float(revenue) if revenue and not pd.isna(revenue) else None,
        'profit': float(net_profit) if net_profit and not pd.isna(net_profit) else None,
        'roe': float(roe) if roe and not pd.isna(roe) else None,
        'pe': float(pe) if pe and not pd.isna(pe) else None,
        'pb': float(pb) if pb and not pd.isna(pb) else None,
        'revenue_growth': float(rev_growth) if rev_growth and not pd.isna(rev_growth) else None,
        'market_cap': float(market_cap) if market_cap and not pd.isna(market_cap) else None,
        'source': 'akshare',
    }


def fetch_stock_info_map() -> dict:
    """获取全市场股票代码-名称映射"""
    import akshare as ak

    df = ak.stock_zh_a_spot_em()
    mapping = {}
    for _, row in df.iterrows():
        code = row['代码']
        name = row['名称']
        if code.startswith('6'):
            mapping[f"{code}.SH"] = name
        elif code.startswith('0') or code.startswith('3'):
            mapping[f"{code}.SZ"] = name
        else:
            mapping[code] = name
    return mapping


def fetch_market_summary() -> dict:
    """获取市场概览（涨跌家数、成交量额）"""
    import akshare as ak

    df = ak.stock_zh_a_spot_em()
    return {
        'total_stocks': len(df),
        'up_count': len(df[df['涨跌幅'] > 0]),
        'down_count': len(df[df['涨跌幅'] < 0]),
        'flat_count': len(df[df['涨跌幅'] == 0]),
        'total_volume': df['成交量'].sum(),
        'total_amount': df['成交额'].sum(),
        'timestamp': datetime.now(),
    }
