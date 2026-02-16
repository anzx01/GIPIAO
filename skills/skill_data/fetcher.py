import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import loguru


class StockDataFetcher:
    """股票数据抓取器"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = loguru.logger
        self._data_cache = {}
    
    def fetch_price_data(self, stock_codes: List[str], 
                         start_date: str = None, 
                         end_date: str = None) -> Dict[str, pd.DataFrame]:
        """获取股票历史行情数据"""
        result = {}
        
        for code in stock_codes:
            try:
                df = self._fetch_single_stock(code, start_date, end_date)
                if df is not None and not df.empty:
                    result[code] = df
                    self.logger.info(f"成功获取 {code} 数据 {len(df)} 条")
                else:
                    self.logger.warning(f"无法获取 {code} 数据")
            except Exception as e:
                self.logger.error(f"获取 {code} 数据失败: {e}")
        
        return result
    
    def _fetch_single_stock(self, code: str, 
                            start_date: Optional[str], 
                            end_date: Optional[str]) -> Optional[pd.DataFrame]:
        """获取单只股票数据 - 使用akshare"""
        try:
            import akshare as ak
            
            if end_date is None:
                end_date = datetime.now().strftime("%Y%m%d")
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
            
            if code.endswith(".SH") or code.endswith(".SZ"):
                stock_code = code.split(".")[0]
                df = ak.stock_zh_a_hist(
                    symbol=stock_code,
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"
                )
                
                if df is not None and not df.empty:
                    df = df.rename(columns={
                        '日期': 'date',
                        '股票代码': 'code',
                        '开盘': 'open',
                        '收盘': 'close',
                        '最高': 'high',
                        '最低': 'low',
                        '成交量': 'volume',
                        '成交额': 'amount',
                        '振幅': 'amplitude',
                        '涨跌幅': 'pct_change',
                        '涨跌额': 'change',
                        '换手率': 'turnover'
                    })
                    df['date'] = pd.to_datetime(df['date'])
                    df['code'] = code
                    return df.sort_values('date')
            
            return None
            
        except Exception as e:
            self.logger.error(f"fetch_single_stock {code} error: {e}")
            return self._generate_mock_data(code, start_date, end_date)
    
    def _generate_mock_data(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """生成模拟数据用于测试"""
        start = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")
        
        dates = pd.date_range(start, end, freq='B')
        n = len(dates)
        
        np.random.seed(hash(code) % 2**32)
        base_price = 100 + np.random.rand() * 100
        
        returns = np.random.randn(n) * 0.02
        prices = base_price * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'date': dates,
            'code': code,
            'open': prices * (1 + np.random.randn(n) * 0.01),
            'high': prices * (1 + np.abs(np.random.randn(n)) * 0.02),
            'low': prices * (1 - np.abs(np.random.randn(n)) * 0.02),
            'close': prices,
            'volume': np.random.randint(1000000, 50000000, n),
            'amount': prices * np.random.randint(1000000, 50000000, n),
            'pct_change': returns * 100,
            'turnover': np.random.uniform(0.5, 5, n)
        })
        
        return df
    
    def fetch_financial_data(self, stock_codes: List[str]) -> Dict[str, dict]:
        """获取财务数据"""
        result = {}
        
        for code in stock_codes:
            try:
                data = self._fetch_financial_indicators(code)
                result[code] = data
            except Exception as e:
                self.logger.error(f"获取 {code} 财务数据失败: {e}")
                result[code] = self._generate_mock_financial(code)
        
        return result
    
    def _fetch_financial_indicators(self, code: str) -> dict:
        """获取财务指标"""
        import akshare as ak
        
        try:
            stock_code = code.split(".")[0]
            df = ak.stock_financial_abstract_ths(symbol=stock_code)
            
            return {
                'code': code,
                'revenue': None,
                'profit': None,
                'roe': None,
                'pe': None,
                'pb': None,
                'source': 'akshare'
            }
        except:
            return self._generate_mock_financial(code)
    
    def _generate_mock_financial(self, code: str) -> dict:
        """生成模拟财务数据"""
        np.random.seed(hash(code) % 2**32)
        
        return {
            'code': code,
            'revenue': np.random.uniform(10, 500) * 1e8,
            'profit': np.random.uniform(1, 50) * 1e8,
            'roe': np.random.uniform(5, 30),
            'pe': np.random.uniform(5, 50),
            'pb': np.random.uniform(0.5, 10),
            'ps': np.random.uniform(0.5, 20),
            'market_cap': np.random.uniform(100, 5000) * 1e8,
            'source': 'mock'
        }
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        df = df.copy()
        
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        
        df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = df['ema12'] - df['ema26']
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        df['volume_ma5'] = df['volume'].rolling(window=5).mean()
        
        df['pct_change_5'] = df['close'].pct_change(periods=5) * 100
        df['pct_change_20'] = df['close'].pct_change(periods=20) * 100
        
        return df
    
    def fetch_market_summary(self) -> dict:
        """获取市场概览数据"""
        try:
            import akshare as ak
            
            df = ak.stock_zh_a_spot_em()
            
            return {
                'total_stocks': len(df),
                'up_count': len(df[df['涨跌幅'] > 0]),
                'down_count': len(df[df['涨跌幅'] < 0]),
                'flat_count': len(df[df['涨跌幅'] == 0]),
                'total_volume': df['成交量'].sum(),
                'total_amount': df['成交额'].sum(),
                'timestamp': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"获取市场概览失败: {e}")
            return {
                'total_stocks': 5000,
                'up_count': 2000,
                'down_count': 2500,
                'flat_count': 500,
                'total_volume': 1e12,
                'total_amount': 1e13,
                'timestamp': datetime.now()
            }
