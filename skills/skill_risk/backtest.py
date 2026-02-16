import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import loguru


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = loguru.logger
        
        self.initial_capital = self.config.get('initial_capital', 1000000)
        self.commission_rate = self.config.get('commission_rate', 0.0003)
        self.slippage = self.config.get('slippage', 0.001)
    
    def run_backtest(self, price_data: Dict[str, pd.DataFrame],
                    portfolio: Dict[str, float],
                    start_date: str = None,
                    end_date: str = None) -> Dict:
        """运行回测"""
        
        if not portfolio:
            return self._empty_result()
        
        start_date, end_date = self._parse_dates(start_date, end_date)
        
        portfolio_values = []
        trades = []
        daily_returns = []
        
        current_capital = self.initial_capital
        holdings = {}
        
        all_dates = self._get_trading_dates(price_data, start_date, end_date)
        
        for i, date in enumerate(all_dates):
            if date < start_date or date > end_date:
                continue
            
            daily_value = current_capital
            for code, weight in portfolio.items():
                if code in price_data:
                    df = price_data[code]
                    price = self._get_price_on_date(df, date)
                    
                    if price is not None:
                        target_value = self.initial_capital * weight
                        shares = target_value / price
                        
                        holdings[code] = {
                            'shares': shares,
                            'cost': price,
                            'weight': weight
                        }
                        
                        daily_value += shares * price
            
            if i > 0:
                prev_value = portfolio_values[-1]['value'] if portfolio_values else self.initial_capital
                daily_return = (daily_value - prev_value) / prev_value
                daily_returns.append(daily_return)
            
            portfolio_values.append({
                'date': date,
                'value': daily_value,
                'return': daily_returns[-1] if daily_returns else 0
            })
        
        result = self._calculate_metrics(portfolio_values, daily_returns)
        
        result['portfolio'] = portfolio
        result['trades'] = trades
        
        return result
    
    def _empty_result(self) -> Dict:
        """返回空结果"""
        return {
            'total_return': 0,
            'annual_return': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
            'win_rate': 0,
            'trades': [],
            'portfolio_values': []
        }
    
    def _parse_dates(self, start_date: Optional[str], 
                    end_date: Optional[str]) -> Tuple:
        """解析日期"""
        if end_date is None:
            end_date = datetime.now()
        elif isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)
        
        if start_date is None:
            start_date = end_date - timedelta(days=252)
        elif isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        
        return start_date, end_date
    
    def _get_trading_dates(self, price_data: Dict[str, pd.DataFrame],
                          start_date, end_date) -> List:
        """获取交易日期"""
        all_dates = set()
        
        for df in price_data.values():
            if not df.empty and 'date' in df.columns:
                dates = df[(df['date'] >= start_date) & (df['date'] <= end_date)]['date']
                all_dates.update(dates.tolist())
        
        return sorted(list(all_dates))
    
    def _get_price_on_date(self, df: pd.DataFrame, date) -> Optional[float]:
        """获取指定日期的价格"""
        if df.empty:
            return None
        
        df_sorted = df.sort_values('date')
        
        exact = df_sorted[df_sorted['date'] == date]
        if not exact.empty:
            return exact.iloc[0]['close']
        
        before = df_sorted[df_sorted['date'] < date]
        if not before.empty:
            return before.iloc[-1]['close']
        
        return None
    
    def _calculate_metrics(self, portfolio_values: List[Dict],
                          daily_returns: List[float]) -> Dict:
        """计算回测指标"""
        
        if not portfolio_values or len(portfolio_values) < 2:
            return self._empty_result()
        
        df = pd.DataFrame(portfolio_values)
        
        total_value = df['value'].iloc[-1]
        total_return = (total_value - self.initial_capital) / self.initial_capital
        
        days = len(df)
        years = days / 252
        annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        df['cummax'] = df['value'].cummax()
        df['drawdown'] = (df['value'] - df['cummax']) / df['cummax']
        max_drawdown = abs(df['drawdown'].min())
        
        if daily_returns:
            returns_array = np.array(daily_returns)
            
            sharpe_ratio = self._calculate_sharpe(returns_array)
            
            win_rate = len(returns_array[returns_array > 0]) / len(returns_array) if len(returns_array) > 0 else 0
            
            volatility = np.std(returns_array) * np.sqrt(252)
            
            sortino = self._calculate_sortino(returns_array)
            
            calmar = annual_return / max_drawdown if max_drawdown > 0 else 0
        else:
            sharpe_ratio = 0
            win_rate = 0
            volatility = 0
            sortino = 0
            calmar = 0
        
        return {
            'start_date': df['date'].iloc[0].strftime('%Y-%m-%d') if hasattr(df['date'].iloc[0], 'strftime') else str(df['date'].iloc[0]),
            'end_date': df['date'].iloc[-1].strftime('%Y-%m-%d') if hasattr(df['date'].iloc[-1], 'strftime') else str(df['date'].iloc[-1]),
            'initial_capital': self.initial_capital,
            'final_value': round(total_value, 2),
            'total_return': round(total_return * 100, 2),
            'annual_return': round(annual_return * 100, 2),
            'max_drawdown': round(max_drawdown * 100, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'sortino_ratio': round(sortino, 2),
            'calmar_ratio': round(calmar, 2),
            'volatility': round(volatility * 100, 2),
            'win_rate': round(win_rate * 100, 2),
            'trading_days': days,
            'portfolio_values': df.to_dict('records')
        }
    
    def _calculate_sharpe(self, returns: np.ndarray, risk_free_rate: float = 0.03) -> float:
        """计算夏普比率"""
        if len(returns) < 2:
            return 0
        
        excess_returns = returns - risk_free_rate / 252
        
        if np.std(returns) == 0:
            return 0
        
        return np.mean(excess_returns) / np.std(returns) * np.sqrt(252)
    
    def _calculate_sortino(self, returns: np.ndarray, 
                          risk_free_rate: float = 0.03) -> float:
        """计算索提诺比率"""
        if len(returns) < 2:
            return 0
        
        excess_returns = returns - risk_free_rate / 252
        
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0 or np.std(downside_returns) == 0:
            return 0
        
        return np.mean(excess_returns) / np.std(downside_returns) * np.sqrt(252)
    
    def compare_strategies(self, results: List[Dict]) -> pd.DataFrame:
        """比较多个策略"""
        if not results:
            return pd.DataFrame()
        
        comparison = []
        
        for i, result in enumerate(results):
            comparison.append({
                'strategy': result.get('name', f'Strategy {i+1}'),
                'total_return': result.get('total_return', 0),
                'annual_return': result.get('annual_return', 0),
                'max_drawdown': result.get('max_drawdown', 0),
                'sharpe_ratio': result.get('sharpe_ratio', 0),
                'win_rate': result.get('win_rate', 0),
                'volatility': result.get('volatility', 0)
            })
        
        return pd.DataFrame(comparison)
