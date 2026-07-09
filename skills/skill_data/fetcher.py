import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import loguru

from .sources import akshare_source
from .sources import BaostockSession


class StockDataFetcher:
    """股票数据抓取器：优先 akshare，失败的代码统一走一次 baostock 兜底"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = loguru.logger
        self._data_cache = {}

    def fetch_price_data(self, stock_codes: List[str],
                         start_date: str = None,
                         end_date: str = None) -> Dict[str, pd.DataFrame]:
        """获取股票历史行情数据"""
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")

        result = {}
        failed_codes = []
        for code in stock_codes:
            try:
                df = akshare_source.fetch_price(code, start_date, end_date)
            except Exception as e:
                self.logger.error(f"akshare 获取 {code} 数据失败: {e}")
                df = None

            if df is not None and not df.empty:
                result[code] = df
                self.logger.info(f"[akshare] 成功获取 {code} 数据 {len(df)} 条")
            else:
                failed_codes.append(code)

        if failed_codes:
            result.update(self._fetch_price_via_baostock(failed_codes, start_date, end_date))

        for code in stock_codes:
            if code not in result:
                self.logger.warning(f"无法获取 {code} 真实行情数据")

        return result

    def _fetch_price_via_baostock(self, codes: List[str], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
        """akshare 兜底：同一会话内批量重试失败的代码"""
        result = {}
        try:
            with BaostockSession() as session:
                for code in codes:
                    df = session.fetch_price(code, start_date, end_date)
                    if df is not None and not df.empty:
                        result[code] = df
                        self.logger.info(f"[baostock] 成功获取 {code} 数据 {len(df)} 条")
                    else:
                        self.logger.warning(f"[baostock] 无法获取 {code} 数据")
        except Exception as e:
            self.logger.error(f"baostock 兜底获取行情数据失败: {e}")
        return result

    def fetch_financial_data(self, stock_codes: List[str]) -> Dict[str, dict]:
        """获取财务数据"""
        spot_data = {}
        try:
            spot_data = akshare_source.fetch_spot_map()
        except Exception as e:
            self.logger.error(f"获取实时行情数据失败: {e}")

        result = {}
        failed_codes = []
        for code in stock_codes:
            try:
                result[code] = akshare_source.fetch_financial(code, spot_data)
            except Exception as e:
                self.logger.error(f"akshare 获取 {code} 财务数据失败: {e}")
                failed_codes.append(code)

        if failed_codes:
            result.update(self._fetch_financial_via_baostock(failed_codes))

        for code in stock_codes:
            if code not in result:
                self.logger.warning(f"无法获取 {code} 真实财务数据")

        return result

    def _fetch_financial_via_baostock(self, codes: List[str]) -> Dict[str, dict]:
        """akshare 兜底：baostock 只能补 PE/PB，其余字段仍为空"""
        result = {}
        try:
            with BaostockSession() as session:
                for code in codes:
                    data = session.fetch_financial(code)
                    if data is not None:
                        result[code] = data
                        self.logger.info(f"[baostock] 成功获取 {code} 财务数据（部分字段）")
        except Exception as e:
            self.logger.error(f"baostock 兜底获取财务数据失败: {e}")
        return result

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        if df is None or df.empty:
            return df

        df = df.copy()

        if 'high' not in df.columns:
            df['high'] = df['close']
        if 'low' not in df.columns:
            df['low'] = df['close']
        if 'volume' not in df.columns:
            df['volume'] = 0

        # 均线
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma60'] = df['close'].rolling(window=60).mean()

        # MACD
        df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = df['ema12'] - df['ema26']
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['hist'] = df['macd'] - df['signal']

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        loss = loss.replace(0, 0.0001) # 避免除以零
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # KDJ
        low_list = df['low'].rolling(window=9).min()
        high_list = df['high'].rolling(window=9).max()
        rsv = (df['close'] - low_list) / (high_list - low_list).replace(0, 0.0001) * 100
        df['k'] = rsv.ewm(com=2).mean()
        df['d'] = df['k'].ewm(com=2).mean()
        df['j'] = 3 * df['k'] - 2 * df['d']

        # 布林带
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)

        # 成交量均线
        df['volume_ma5'] = df['volume'].rolling(window=5).mean()
        df['volume_ma10'] = df['volume'].rolling(window=10).mean()

        # 涨跌幅
        df['pct_change_5'] = df['close'].pct_change(periods=5) * 100
        df['pct_change_20'] = df['close'].pct_change(periods=20) * 100

        return df

    def get_stock_info_map(self) -> Dict[str, str]:
        """获取所有股票代码和名称的映射"""
        try:
            mapping = akshare_source.fetch_stock_info_map()
            if mapping:
                return mapping
        except Exception as e:
            self.logger.error(f"akshare 获取股票列表失败: {e}")

        try:
            with BaostockSession() as session:
                mapping = session.fetch_stock_info_map()
                if mapping:
                    self.logger.info(f"[baostock] 成功获取股票列表 {len(mapping)} 条")
                    return mapping
        except Exception as e:
            self.logger.error(f"baostock 兜底获取股票列表失败: {e}")

        return {}

    def fetch_market_summary(self) -> dict:
        """获取市场概览数据（依赖实时快照，baostock 无对应接口，无法兜底）"""
        try:
            return akshare_source.fetch_market_summary()
        except Exception as e:
            self.logger.error(f"获取市场概览失败: {e}")
            raise
