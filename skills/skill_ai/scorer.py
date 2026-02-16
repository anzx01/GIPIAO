import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import loguru


class StockScorer:
    """股票评分引擎"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = loguru.logger
        
        self.factor_weights = {
            'pe_ratio': 0.15,
            'pb_ratio': 0.10,
            'roe': 0.20,
            'revenue_growth': 0.15,
            'momentum': 0.20,
            'volatility': 0.10,
            'liquidity': 0.10
        }
        
        if 'factors' in self.config and isinstance(self.config['factors'], dict):
            self.factor_weights.update(self.config['factors'])
    
    def score_stocks(self, price_data: Dict[str, pd.DataFrame],
                    financial_data: Dict[str, dict],
                    news_data: Dict[str, List[dict]]) -> pd.DataFrame:
        """对股票进行综合评分"""
        
        results = []
        
        for code, df in price_data.items():
            try:
                score = self._calculate_score(
                    code, df, 
                    financial_data.get(code, {}),
                    news_data.get(code, [])
                )
                results.append(score)
            except Exception as e:
                self.logger.error(f"评分 {code} 失败: {e}")
        
        if not results:
            return pd.DataFrame()
        
        df_scores = pd.DataFrame(results)
        
        df_scores = df_scores.sort_values('total_score', ascending=False)
        df_scores['rank'] = range(1, len(df_scores) + 1)
        
        return df_scores
    
    def _calculate_score(self, code: str, price_df: pd.DataFrame,
                        financial: dict, news: list) -> dict:
        """计算单只股票的综合评分"""
        
        factor_scores = {}
        
        factor_scores['pe_score'] = self._score_pe(financial.get('pe', 20))
        factor_scores['pb_score'] = self._score_pb(financial.get('pb', 3))
        factor_scores['roe_score'] = self._score_roe(financial.get('roe', 10))
        
        factor_scores['momentum_score'] = self._score_momentum(price_df)
        factor_scores['volatility_score'] = self._score_volatility(price_df)
        factor_scores['liquidity_score'] = self._score_liquidity(price_df)
        
        if news:
            factor_scores['sentiment_score'] = self._score_sentiment(news)
        else:
            factor_scores['sentiment_score'] = 50
        
        total_score = sum(
            factor_scores[k] * self.factor_weights.get(k.replace('_score', ''), 0.1)
            for k in factor_scores
        )
        
        return {
            'code': code,
            'total_score': round(total_score, 2),
            **factor_scores,
            'pe': financial.get('pe'),
            'pb': financial.get('pb'),
            'roe': financial.get('roe'),
            'market_cap': financial.get('market_cap'),
            'timestamp': datetime.now()
        }
    
    def _score_pe(self, pe: float) -> float:
        """PE估值评分 (0-100, 越低越好)"""
        if pe is None or pe <= 0:
            return 50
        
        if pe < 10:
            return 100
        elif pe < 20:
            return 80
        elif pe < 30:
            return 60
        elif pe < 50:
            return 40
        else:
            return 20
    
    def _score_pb(self, pb: float) -> float:
        """PB估值评分 (0-100, 越低越好)"""
        if pb is None or pb <= 0:
            return 50
        
        if pb < 1:
            return 100
        elif pb < 2:
            return 80
        elif pb < 3:
            return 60
        elif pb < 5:
            return 40
        else:
            return 20
    
    def _score_roe(self, roe: float) -> float:
        """ROE盈利能力评分 (0-100, 越高越好)"""
        if roe is None:
            return 50
        
        if roe > 25:
            return 100
        elif roe > 20:
            return 85
        elif roe > 15:
            return 70
        elif roe > 10:
            return 55
        elif roe > 5:
            return 40
        else:
            return 20
    
    def _score_momentum(self, df: pd.DataFrame) -> float:
        """动量评分 (0-100)"""
        if df is None or len(df) < 20:
            return 50
        
        recent = df.tail(20)
        
        ma5 = recent['close'].iloc[-5:].mean()
        ma20 = recent['close'].mean()
        
        if ma5 > ma20 * 1.05:
            return 80
        elif ma5 > ma20:
            return 60
        elif ma5 > ma20 * 0.95:
            return 40
        else:
            return 20
    
    def _score_volatility(self, df: pd.DataFrame) -> float:
        """波动性评分 (0-100, 适中最好)"""
        if df is None or len(df) < 20:
            return 50
        
        returns = df['close'].pct_change().dropna()
        
        if len(returns) < 5:
            return 50
        
        volatility = returns.std() * np.sqrt(252)
        
        if volatility < 0.15:
            return 100
        elif volatility < 0.25:
            return 80
        elif volatility < 0.35:
            return 60
        elif volatility < 0.5:
            return 40
        else:
            return 20
    
    def _score_liquidity(self, df: pd.DataFrame) -> float:
        """流动性评分 (0-100)"""
        if df is None or len(df) < 5:
            return 50
        
        recent = df.tail(20)
        
        avg_volume = recent['volume'].mean()
        
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
    
    def _score_sentiment(self, news: List[dict]) -> float:
        """情绪评分 (0-100)"""
        if not news:
            return 50
        
        scores = [n.get('sentiment_score', 0) for n in news]
        
        avg = sum(scores) / len(scores)
        
        normalized = (avg + 1) / 2 * 100
        
        return max(0, min(100, normalized))
    
    def get_top_stocks(self, scores: pd.DataFrame, n: int = 10) -> List[str]:
        """获取评分最高的N只股票"""
        if scores.empty:
            return []
        
        return scores.head(n)['code'].tolist()
    
    def generate_recommendation(self, code: str, score: float) -> str:
        """生成买入建议"""
        if score >= 80:
            return "强烈推荐买入"
        elif score >= 65:
            return "建议买入"
        elif score >= 50:
            return "持有观望"
        elif score >= 35:
            return "建议减仓"
        else:
            return "建议卖出"
