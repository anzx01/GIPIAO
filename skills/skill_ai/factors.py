import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import loguru


class FactorModel:
    """多因子选股模型"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = loguru.logger
        
        self.factors = [
            'value',
            'quality',
            'momentum',
            'volatility',
            'size',
            'liquidity'
        ]
    
    def calculate_factors(self, price_data: Dict[str, pd.DataFrame],
                         financial_data: Dict[str, dict]) -> pd.DataFrame:
        """计算所有因子值"""
        
        factor_results = []
        
        for code, df in price_data.items():
            factors = self._calculate_single_factors(
                code, df, financial_data.get(code, {})
            )
            factor_results.append(factors)
        
        if not factor_results:
            return pd.DataFrame()
        
        df_factors = pd.DataFrame(factor_results)
        
        for factor in self.factors:
            col = f'{factor}_score'
            if col in df_factors.columns:
                df_factors[col] = self._normalize_factor(df_factors[col])
        
        return df_factors
    
    def _calculate_single_factors(self, code: str, 
                                  price_df: pd.DataFrame,
                                  financial: dict) -> dict:
        """计算单只股票的因子值"""
        
        result = {'code': code}
        
        result['value_score'] = self._factor_value(financial)
        result['quality_score'] = self._factor_quality(financial)
        result['momentum_score'] = self._factor_momentum(price_df)
        result['volatility_score'] = self._factor_volatility(price_df)
        result['size_score'] = self._factor_size(financial)
        result['liquidity_score'] = self._factor_liquidity(price_df)
        
        return result
    
    def _factor_value(self, financial: dict) -> float:
        """价值因子 - 基于PE/PB"""
        pe = financial.get('pe', 20)
        pb = financial.get('pb', 3)
        
        if pe is None or pe <= 0:
            pe = 20
        if pb is None or pb <= 0:
            pb = 3
        
        pe_score = 1 / np.log(pe + 1) if pe > 0 else 0.5
        pb_score = 1 / np.log(pb + 1) if pb > 0 else 0.5
        
        return (pe_score * 0.6 + pb_score * 0.4) * 100
    
    def _factor_quality(self, financial: dict) -> float:
        """质量因子 - 基于ROE/利润率"""
        roe = financial.get('roe', 10)
        profit = financial.get('profit', 0)
        revenue = financial.get('revenue', 1)
        
        if roe is None:
            roe = 10
        
        profit_margin = profit / revenue if revenue > 0 else 0.1
        
        roe_score = min(100, roe * 4)
        margin_score = min(100, profit_margin * 100 * 2)
        
        return roe_score * 0.7 + margin_score * 0.3
    
    def _factor_momentum(self, df: pd.DataFrame) -> float:
        """动量因子"""
        if df is None or len(df) < 60:
            return 50
        
        returns_20d = (df['close'].iloc[-1] / df['close'].iloc[-21] - 1) if len(df) > 20 else 0
        returns_60d = (df['close'].iloc[-1] / df['close'].iloc[-61] - 1) if len(df) > 60 else returns_20d
        
        mom_20 = min(100, max(0, 50 + returns_20d * 500))
        mom_60 = min(100, max(0, 50 + returns_60d * 300))
        
        return mom_20 * 0.6 + mom_60 * 0.4
    
    def _factor_volatility(self, df: pd.DataFrame) -> float:
        """波动率因子 - 低波动更好"""
        if df is None or len(df) < 20:
            return 50
        
        returns = df['close'].pct_change().dropna()
        
        if len(returns) < 10:
            return 50
        
        vol = returns.std() * np.sqrt(252)
        
        if vol < 0.1:
            return 100
        elif vol < 0.2:
            return 80
        elif vol < 0.3:
            return 60
        elif vol < 0.5:
            return 40
        else:
            return 20
    
    def _factor_size(self, financial: dict) -> float:
        """规模因子"""
        market_cap = financial.get('market_cap', 1e10)
        
        if market_cap > 1e11:
            return 80
        elif market_cap > 5e10:
            return 70
        elif market_cap > 1e10:
            return 60
        elif market_cap > 5e9:
            return 50
        else:
            return 40
    
    def _factor_liquidity(self, df: pd.DataFrame) -> float:
        """流动性因子"""
        if df is None or len(df) < 20:
            return 50
        
        avg_volume = df['volume'].tail(20).mean()
        
        if avg_volume > 1e8:
            return 100
        elif avg_volume > 5e7:
            return 80
        elif avg_volume > 1e7:
            return 60
        elif avg_volume > 5e6:
            return 40
        else:
            return 20
    
    def _normalize_factor(self, series: pd.Series) -> pd.Series:
        """因子标准化 (0-100)"""
        min_val = series.min()
        max_val = series.max()
        
        if max_val - min_val == 0:
            return pd.Series([50] * len(series), index=series.index)
        
        normalized = (series - min_val) / (max_val - min_val) * 100
        
        return normalized
    
    def calculate_composite_score(self, df_factors: pd.DataFrame,
                                  weights: Dict[str, float] = None) -> pd.DataFrame:
        """计算综合得分"""
        
        if df_factors.empty:
            return df_factors
        
        if weights is None:
            weights = {f: 1/len(self.factors) for f in self.factors}
        
        df_factors = df_factors.copy()
        
        df_factors['composite_score'] = 0
        
        for factor in self.factors:
            col = f'{factor}_score'
            if col in df_factors.columns:
                weight = weights.get(factor, 1/len(self.factors))
                df_factors['composite_score'] += df_factors[col] * weight
        
        df_factors = df_factors.sort_values('composite_score', ascending=False)
        df_factors['rank'] = range(1, len(df_factors) + 1)
        
        return df_factors
    
    def select_by_factors(self, df_factors: pd.DataFrame,
                         top_n: int = 10,
                         min_score: float = 50) -> List[str]:
        """根据因子选择股票"""
        
        if df_factors.empty:
            return []
        
        df_filtered = df_factors[
            (df_factors['composite_score'] >= min_score)
        ].head(top_n)
        
        return df_filtered['code'].tolist()
