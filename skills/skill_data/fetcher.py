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
            from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

            if end_date is None:
                end_date = datetime.now().strftime("%Y%m%d")
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")

            if code.endswith(".SH") or code.endswith(".SZ"):
                stock_code = code.split(".")[0]

                # 使用线程池执行，设置10秒超时
                def fetch_data():
                    return ak.stock_zh_a_hist(
                        symbol=stock_code,
                        start_date=start_date,
                        end_date=end_date,
                        adjust="qfq"
                    )

                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(fetch_data)
                    try:
                        df = future.result(timeout=10)  # 10秒超时
                    except FutureTimeoutError:
                        self.logger.error(f"获取 {code} 数据超时（10秒）")
                        return None
                
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
            return None
    
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
        
        # 预先获取实时行情数据以提取PE/PB
        spot_data = {}
        try:
            import akshare as ak
            spot_df = ak.stock_zh_a_spot_em()
            for _, row in spot_df.iterrows():
                spot_data[row['代码']] = {
                    'pe': row.get('市盈率-动态'),
                    'pb': row.get('市净率'),
                    'market_cap': row.get('总市值')
                }
        except Exception as e:
            self.logger.error(f"获取实时行情数据失败: {e}")

        for code in stock_codes:
            try:
                data = self._fetch_financial_indicators(code, spot_data)
                result[code] = data
            except Exception as e:
                self.logger.error(f"获取 {code} 财务数据失败: {e}")
                result[code] = self._generate_mock_financial(code)
        
        return result
    
    def _fetch_financial_indicators(self, code: str, spot_data: dict = None) -> dict:
        """获取财务指标"""
        import akshare as ak
        
        try:
            stock_code = code.split(".")[0]
            
            # 从预取的行情数据中获取PE/PB
            pe = None
            pb = None
            market_cap = None
            if spot_data and stock_code in spot_data:
                pe = spot_data[stock_code].get('pe')
                pb = spot_data[stock_code].get('pb')
                market_cap = spot_data[stock_code].get('market_cap')

            # 获取主要财务指标 (ROE, 营收增长等)
            roe = None
            rev_growth = None
            net_profit = None
            revenue = None
            
            try:
                # 使用 stock_financial_analysis_indicator 获取关键指标
                finance_df = ak.stock_financial_analysis_indicator(symbol=stock_code)
                if not finance_df.empty:
                    latest = finance_df.iloc[0]
                    roe = latest.get('净资产收益率(%)')
                    rev_growth = latest.get('营业收入同比增长率(%)')
                    net_profit = latest.get('净利润(元)')
                    revenue = latest.get('营业收入(元)')
            except Exception as e:
                self.logger.warning(f"获取 {code} 详细财务指标失败: {e}")

            return {
                'code': code,
                'revenue': float(revenue) if revenue and not pd.isna(revenue) else None,
                'profit': float(net_profit) if net_profit and not pd.isna(net_profit) else None,
                'roe': float(roe) if roe and not pd.isna(roe) else None,
                'pe': float(pe) if pe and not pd.isna(pe) else None,
                'pb': float(pb) if pb and not pd.isna(pb) else None,
                'revenue_growth': float(rev_growth) if rev_growth and not pd.isna(rev_growth) else None,
                'market_cap': float(market_cap) if market_cap and not pd.isna(market_cap) else None,
                'source': 'akshare'
            }
        except Exception as e:
            self.logger.error(f"解析 {code} 财务数据失败: {e}")
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
        if df is None or df.empty:
            return df
            
        df = df.copy()
        
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
            import akshare as ak
            df = ak.stock_zh_a_spot_em()
            mapping = {}
            for _, row in df.iterrows():
                code = row['代码']
                name = row['名称']
                # 简单处理：6开头的加.SH，0/3开头的加.SZ
                if code.startswith('6'):
                    mapping[f"{code}.SH"] = name
                elif code.startswith('0') or code.startswith('3'):
                    mapping[f"{code}.SZ"] = name
                else:
                    mapping[code] = name
            return mapping
        except Exception as e:
            self.logger.error(f"获取股票列表失败: {e}")
            return {}
    
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
