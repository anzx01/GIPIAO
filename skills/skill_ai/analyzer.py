import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import loguru


class StrategyAnalyzer:
    """策略分析器"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = loguru.logger
    
    def analyze_strategy(self, price_data: Dict[str, pd.DataFrame],
                        stock_list: List[str]) -> Dict:
        """分析选股策略表现"""
        
        results = {
            'total_stocks': len(stock_list),
            'analysis_date': datetime.now().strftime("%Y-%m-%d"),
            'stocks': []
        }
        
        for code in stock_list:
            if code in price_data:
                df = price_data[code]
                analysis = self._analyze_single_stock(df)
                results['stocks'].append(analysis)
        
        if results['stocks']:
            df_analysis = pd.DataFrame(results['stocks'])
            
            results['summary'] = {
                'avg_return_5d': df_analysis['return_5d'].mean(),
                'avg_return_20d': df_analysis['return_20d'].mean(),
                'avg_volatility': df_analysis['volatility'].mean(),
                'avg_score': df_analysis['signal_score'].mean(),
                'best_performer': df_analysis.loc[df_analysis['return_20d'].idxmax(), 'code'],
                'worst_performer': df_analysis.loc[df_analysis['return_20d'].idxmin(), 'code']
            }
        
        return results
    
    def _analyze_single_stock(self, df: pd.DataFrame) -> dict:
        """分析单只股票"""
        
        if df is None or len(df) < 30:
            return {
                'code': df['code'].iloc[0] if df is not None and len(df) > 0 else 'unknown',
                'return_5d': 0,
                'return_20d': 0,
                'volatility': 0,
                'signal': 'hold',
                'signal_score': 50
            }
        
        close = df['close']
        
        return_5d = (close.iloc[-1] / close.iloc[-6] - 1) * 100 if len(df) > 5 else 0
        return_20d = (close.iloc[-1] / close.iloc[-21] - 1) * 100 if len(df) > 20 else 0
        
        returns = close.pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100
        
        signal, score = self._generate_signal(df)
        
        return {
            'code': df['code'].iloc[0],
            'current_price': close.iloc[-1],
            'return_5d': round(return_5d, 2),
            'return_20d': round(return_20d, 2),
            'volatility': round(volatility, 2),
            'ma5': round(close.iloc[-5:].mean(), 2),
            'ma20': round(close.iloc[-20:].mean(), 2),
            'signal': signal,
            'signal_score': round(score, 2)
        }
    
    def _generate_signal(self, df: pd.DataFrame) -> Tuple[str, float]:
        """生成交易信号"""
        
        if len(df) < 30:
            return 'hold', 50
        
        close = df['close']
        
        ma5 = close.iloc[-5:].mean()
        ma10 = close.iloc[-10:].mean()
        ma20 = close.iloc[-20:].mean()
        current = close.iloc[-1]
        
        rsi = self._calculate_rsi(close)
        
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal_line = macd.ewm(span=9, adjust=False).mean()
        
        score = 50
        
        if ma5 > ma10 > ma20:
            score += 20
        elif ma5 > ma20:
            score += 10
        
        if current > ma5:
            score += 10
        
        if rsi < 30:
            score += 15
        elif rsi > 70:
            score -= 15
        elif rsi < 50:
            score += 5
        
        if macd > signal_line:
            score += 10
        else:
            score -= 5
        
        score = max(0, min(100, score))
        
        if score >= 70:
            signal = 'buy'
        elif score <= 30:
            signal = 'sell'
        else:
            signal = 'hold'
        
        return signal, score
    
    def _calculate_rsi(self, series: pd.Series, period: int = 14) -> float:
        """计算RSI指标"""
        if len(series) < period + 1:
            return 50
        
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    def compare_strategies(self, price_data: Dict[str, pd.DataFrame],
                          portfolio_a: List[str],
                          portfolio_b: List[str],
                          days: int = 30) -> Dict:
        """比较两个策略的表现"""
        
        perf_a = self._calculate_portfolio_performance(price_data, portfolio_a, days)
        perf_b = self._calculate_portfolio_performance(price_data, portfolio_b, days)
        
        return {
            'period_days': days,
            'portfolio_a': perf_a,
            'portfolio_b': perf_b,
            'winner': 'A' if perf_a['return'] > perf_b['return'] else 'B',
            'return_diff': perf_a['return'] - perf_b['return']
        }
    
    def _calculate_portfolio_performance(self, price_data: Dict[str, pd.DataFrame],
                                        stocks: List[str], days: int) -> dict:
        """计算组合表现"""
        
        if not stocks:
            return {'return': 0, 'volatility': 0, 'sharpe': 0}
        
        returns = []
        
        for code in stocks:
            if code in price_data:
                df = price_data[code]
                if len(df) >= days:
                    ret = (df['close'].iloc[-1] / df['close'].iloc[-days] - 1)
                    returns.append(ret)
        
        if not returns:
            return {'return': 0, 'volatility': 0, 'sharpe': 0}
        
        avg_return = np.mean(returns) * 100
        volatility = np.std(returns) * np.sqrt(252) * 100
        
        sharpe = avg_return / volatility if volatility > 0 else 0
        
        return {
            'return': round(avg_return, 2),
            'volatility': round(volatility, 2),
            'sharpe': round(sharpe, 2),
            'stocks_count': len(returns)
        }
    
    def optimize_weights(self, price_data: Dict[str, pd.DataFrame],
                       stocks: List[str], risk_free_rate: float = 0.03) -> Dict:
        """优化投资组合权重"""
        
        if not stocks or len(stocks) < 2:
            return {'weights': {}, 'expected_return': 0, 'expected_volatility': 0}
        
        returns_data = []
        
        for code in stocks:
            if code in price_data:
                df = price_data[code]
                if len(df) >= 30:
                    ret = df['close'].pct_change().dropna()
                    returns_data.append(ret)
        
        if len(returns_data) < 2:
            return {'weights': {}, 'expected_return': 0, 'expected_volatility': 0}
        
        returns_df = pd.concat(returns_data, axis=1)
        returns_df.columns = stocks[:len(returns_data)]
        
        mean_returns = returns_df.mean() * 252
        cov_matrix = returns_df.cov() * 252
        
        n = len(mean_returns)
        equal_weights = np.array([1/n] * n)
        
        portfolio_return = np.dot(equal_weights, mean_returns)
        portfolio_volatility = np.sqrt(np.dot(equal_weights, np.dot(cov_matrix, equal_weights)))
        
        sharpe = (portfolio_return - risk_free_rate) / portfolio_volatility
        
        weights_dict = {
            stocks[i]: round(equal_weights[i] * 100, 2) 
            for i in range(len(stocks))
        }
        
        return {
            'weights': weights_dict,
            'expected_return': round(portfolio_return * 100, 2),
            'expected_volatility': round(portfolio_volatility * 100, 2),
            'sharpe_ratio': round(sharpe, 2)
        }
