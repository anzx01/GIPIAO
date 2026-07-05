"""baostock 数据源封装（akshare 限流/失效时的兜底数据源）

baostock 只提供日线级别的历史行情和估值数据，没有实时快照，
因此仅用于给 akshare 的失败请求兜底，无法替代 fetch_market_summary 这类实时市场概览。
"""
from datetime import datetime
from typing import Optional

import pandas as pd
import loguru

logger = loguru.logger


def _to_baostock_code(code: str) -> Optional[str]:
    """平台代码格式（600000.SH / 000001.SZ）转换为 baostock 格式（sh.600000 / sz.000001）"""
    if code.endswith(".SH"):
        return f"sh.{code.split('.')[0]}"
    if code.endswith(".SZ"):
        return f"sz.{code.split('.')[0]}"
    return None


def _to_dashed_date(yyyymmdd: str) -> str:
    """akshare 风格的 YYYYMMDD 转换为 baostock 要求的 YYYY-MM-DD"""
    return datetime.strptime(yyyymmdd, "%Y%m%d").strftime("%Y-%m-%d")


class BaostockSession:
    """baostock 要求显式登录/登出，会话内复用同一次登录以避免重复握手"""

    def __enter__(self):
        import baostock as bs

        result = bs.login()
        if result.error_code != '0':
            raise ConnectionError(f"baostock 登录失败: {result.error_msg}")
        self._bs = bs
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._bs.logout()

    def fetch_price(self, code: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """获取单只股票历史行情（前复权）"""
        bs_code = _to_baostock_code(code)
        if bs_code is None:
            return None

        rs = self._bs.query_history_k_data_plus(
            bs_code, "date,open,high,low,close,volume,amount,turn,pctChg",
            start_date=_to_dashed_date(start_date), end_date=_to_dashed_date(end_date),
            frequency="d", adjustflag="2",
        )
        if rs.error_code != '0':
            logger.error(f"baostock 获取 {code} 数据失败: {rs.error_msg}")
            return None

        rows = []
        while rs.next():
            rows.append(rs.get_row_data())
        if not rows:
            return None

        df = pd.DataFrame(rows, columns=rs.fields)
        numeric_cols = ["open", "high", "low", "close", "volume", "amount", "turn", "pctChg"]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
        df = df.rename(columns={'turn': 'turnover', 'pctChg': 'pct_change'})
        df['date'] = pd.to_datetime(df['date'])
        df['code'] = code
        df['change'] = df['close'].diff()
        df['amplitude'] = (df['high'] - df['low']) / df['close'].shift(1) * 100
        return df.sort_values('date')

    def fetch_financial(self, code: str) -> Optional[dict]:
        """获取财务指标：仅 PE/PB 取自最新交易日估值字段，ROE/营收等 baostock 无稳定接口，留空由 mock 兜底"""
        bs_code = _to_baostock_code(code)
        if bs_code is None:
            return None

        rs = self._bs.query_history_k_data_plus(
            bs_code, "date,peTTM,pbMRQ", frequency="d", adjustflag="2",
        )
        if rs.error_code != '0':
            logger.error(f"baostock 获取 {code} 估值数据失败: {rs.error_msg}")
            return None

        pe = pb = None
        while rs.next():
            row = rs.get_row_data()
            pe = pd.to_numeric(row[1], errors='coerce')
            pb = pd.to_numeric(row[2], errors='coerce')

        return {
            'code': code,
            'revenue': None,
            'profit': None,
            'roe': None,
            'pe': float(pe) if pe is not None and not pd.isna(pe) else None,
            'pb': float(pb) if pb is not None and not pd.isna(pb) else None,
            'revenue_growth': None,
            'market_cap': None,
            'source': 'baostock',
        }

    def fetch_stock_info_map(self) -> dict:
        """获取全市场股票代码-名称映射（沪深 A 股，剔除已退市）"""
        rs = self._bs.query_stock_basic()
        mapping = {}
        while rs.next():
            row = rs.get_row_data()
            bs_code, code_name, _ipo_date, _out_date, stock_type, status = row[:6]
            if stock_type != '1' or status != '1':
                continue
            market, num = bs_code.split('.')
            suffix = 'SH' if market == 'sh' else 'SZ'
            mapping[f"{num}.{suffix}"] = code_name
        return mapping
