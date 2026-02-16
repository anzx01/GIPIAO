import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import loguru


class RiskMetrics:
    """风险指标计算"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = loguru.logger
    
    def calculate_all_metrics(self, returns: pd.Series) -> Dict:
        """计算所有风险指标"""
        
        if returns is None or len(returns) < 2:
            return self._default_metrics()
        
        returns = returns.dropna()
        
        if len(returns) < 2:
            return self._default_metrics()
        
        metrics = {
            'volatility': self._volatility(returns),
            'var_95': self._var(returns, 0.95),
            'var_99': self._var(returns, 0.99),
            'cvar_95': self._cvar(returns, 0.95),
            'cvar_99': self._cvar(returns, 0.99),
            'max_drawdown': self._max_drawdown(returns),
            'skewness': self._skewness(returns),
            'kurtosis': self._kurtosis(returns),
            'beta': None,
            'correlation': None
        }
        
        return metrics
    
    def _default_metrics(self) -> Dict:
        """默认风险指标"""
        return {
            'volatility': 0,
            'var_95': 0,
            'var_99': 0,
            'cvar_95': 0,
            'cvar_99': 0,
            'max_drawdown': 0,
            'skewness': 0,
            'kurtosis': 0,
            'beta': None,
            'correlation': None
        }
    
    def _volatility(self, returns: pd.Series) -> float:
        """年化波动率"""
        if len(returns) < 2:
            return 0
        
        return returns.std() * np.sqrt(252)
    
    def _var(self, returns: pd.Series, confidence: float) -> float:
        """风险价值 (VaR)"""
        if len(returns) < 2:
            return 0
        
        return np.percentile(returns, (1 - confidence) * 100)
    
    def _cvar(self, returns: pd.Series, confidence: float) -> float:
        """条件风险价值 (CVaR/ES)"""
        if len(returns) < 2:
            return 0
        
        var = self._var(returns, confidence)
        return returns[returns <= var].mean()
    
    def _max_drawdown(self, returns: pd.Series) -> float:
        """最大回撤"""
        if len(returns) < 2:
            return 0
        
        wealth_index = (1 + returns).cumprod()
        previous_peaks = wealth_index.cummax()
        drawdowns = (wealth_index - previous_peaks) / previous_peaks
        
        return abs(drawdowns.min())
    
    def _skewness(self, returns: pd.Series) -> float:
        """偏度"""
        if len(returns) < 3:
            return 0
        
        return returns.skew()
    
    def _kurtosis(self, returns: pd.Series) -> float:
        """峰度"""
        if len(returns) < 4:
            return 0
        
        return returns.kurtosis()
    
    def calculate_portfolio_risk(self, returns_dict: Dict[str, pd.Series],
                                 weights: Dict[str, float]) -> Dict:
        """计算投资组合风险"""
        
        if not returns_dict or not weights:
            return self._default_metrics()
        
        aligned_returns = []
        
        for code in weights.keys():
            if code in returns_dict:
                aligned_returns.append(returns_dict[code])
        
        if not aligned_returns:
            return self._default_metrics()
        
        min_length = min(len(r) for r in aligned_returns)
        
        aligned_returns = [r.tail(min_length) for r in aligned_returns]
        
        df_returns = pd.concat(aligned_returns, axis=1)
        df_returns.columns = list(weights.keys())[:len(aligned_returns)]
        
        weight_array = np.array([weights.get(code, 0) for code in df_returns.columns])
        weight_array = weight_array / weight_array.sum()
        
        portfolio_returns = (df_returns * weight_array).sum(axis=1)
        
        return self.calculate_all_metrics(portfolio_returns)
    
    def calculate_beta(self, stock_returns: pd.Series, 
                       market_returns: pd.Series) -> float:
        """计算Beta"""
        if len(stock_returns) < 2 or len(market_returns) < 2:
            return 1.0
        
        min_len = min(len(stock_returns), len(market_returns))
        
        stock = stock_returns.tail(min_len).values
        market = market_returns.tail(min_len).values
        
        covariance = np.cov(stock, market)[0][1]
        market_variance = np.var(market)
        
        if market_variance == 0:
            return 1.0
        
        return covariance / market_variance
    
    def calculate_correlation(self, returns_a: pd.Series,
                             returns_b: pd.Series) -> float:
        """计算相关系数"""
        if len(returns_a) < 2 or len(returns_b) < 2:
            return 0
        
        min_len = min(len(returns_a), len(returns_b))
        
        return returns_a.tail(min_len).corr(returns_b.tail(min_len))
    
    def risk_report(self, portfolio_returns: pd.Series,
                   benchmark_returns: pd.Series = None) -> Dict:
        """生成风险报告"""
        
        metrics = self.calculate_all_metrics(portfolio_returns)
        
        report = {
            'risk_level': self._assess_risk_level(metrics),
            'metrics': metrics,
            'recommendations': self._generate_recommendations(metrics)
        }
        
        if benchmark_returns is not None:
            beta = self.calculate_beta(portfolio_returns, benchmark_returns)
            correlation = self.calculate_correlation(portfolio_returns, benchmark_returns)
            
            report['vs_benchmark'] = {
                'beta': round(beta, 2),
                'correlation': round(correlation, 2)
            }
        
        return report
    
    def _assess_risk_level(self, metrics: Dict) -> str:
        """评估风险等级"""
        volatility = metrics.get('volatility', 0)
        max_dd = metrics.get('max_drawdown', 0)
        
        if volatility > 0.4 or max_dd > 0.4:
            return '高风险'
        elif volatility > 0.25 or max_dd > 0.25:
            return '中等风险'
        else:
            return '低风险'
    
    def _generate_recommendations(self, metrics: Dict) -> List[str]:
        """生成风险建议"""
        recommendations = []
        
        volatility = metrics.get('volatility', 0)
        if volatility > 0.4:
            recommendations.append("波动率过高，建议降低仓位或分散投资")
        elif volatility > 0.25:
            recommendations.append("波动率偏高，建议关注风险控制")
        
        max_dd = metrics.get('max_drawdown', 0)
        if max_dd > 0.3:
            recommendations.append("最大回撤较大，建议设置止损")
        
        var_95 = metrics.get('var_95', 0)
        if var_95 < -0.05:
            recommendations.append("VaR较高，可能存在较大下行风险")
        
        skewness = metrics.get('skewness', 0)
        if skewness < -1:
            recommendations.append("收益分布左偏，存在较大尾部风险")
        
        if not recommendations:
            recommendations.append("风险指标正常，继续保持当前策略")
        
        return recommendations
