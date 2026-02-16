import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import loguru


class NewsFetcher:
    """新闻和舆情数据抓取器"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = loguru.logger
    
    def fetch_news(self, stock_codes: List[str], 
                   days: int = 7) -> Dict[str, List[dict]]:
        """获取股票相关新闻"""
        result = {}
        
        for code in stock_codes:
            try:
                news = self._fetch_stock_news(code, days)
                result[code] = news
            except Exception as e:
                self.logger.error(f"获取 {code} 新闻失败: {e}")
                result[code] = self._generate_mock_news(code, days)
        
        return result
    
    def _fetch_stock_news(self, code: str, days: int) -> List[dict]:
        """获取单只股票新闻"""
        try:
            import akshare as ak
            
            stock_code = code.split(".")[0]
            
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
            
            df = ak.stock_news_em(symbol=stock_code)
            
            if df is not None and not df.empty:
                news_list = []
                for _, row in df.iterrows():
                    news_list.append({
                        'title': row.get('新闻标题', ''),
                        'url': row.get('新闻链接', ''),
                        'datetime': str(row.get('发布时间', '')),
                        'source': row.get('文章来源', ''),
                        'code': code
                    })
                return news_list
            
            return self._generate_mock_news(code, days)
            
        except Exception as e:
            self.logger.warning(f"fetch_news {code}: {e}")
            return self._generate_mock_news(code, days)
    
    def _generate_mock_news(self, code: str, days: int) -> List[dict]:
        """生成模拟新闻数据"""
        stock_name = code.split('.')[0]
        
        titles = [
            f"{stock_name} 发布最新季度财报，营收同比增长",
            f"分析师上调 {stock_name} 目标价",
            f"{stock_name} 获得重要战略合作机会",
            f"机构投资者大举买入 {stock_name} 股票",
            f"{stock_name} 宣布新产品研发计划",
            f"市场看好 {stock_name} 未来发展前景",
            f"{stock_name} 股价突破关键技术位",
        ]
        
        news_list = []
        base_date = datetime.now()
        
        for i in range(min(days * 3, 15)):
            date = base_date - timedelta(hours=i * 8 + random.randint(0, 12))
            
            news_list.append({
                'title': random.choice(titles) + f" {random.randint(5, 25)}%",
                'url': f"https://example.com/news/{code}/{i}",
                'datetime': date.strftime("%Y-%m-%d %H:%M:%S"),
                'source': random.choice(['证券日报', '第一财经', '华尔街日报', '彭博社']),
                'code': code,
                'sentiment': random.choice(['positive', 'neutral', 'negative']),
                'sentiment_score': random.uniform(-1, 1)
            })
        
        return news_list
    
    def analyze_sentiment(self, news_list: List[dict]) -> dict:
        """分析新闻情绪"""
        if not news_list:
            return {
                'sentiment': 'neutral',
                'score': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }
        
        scores = [n.get('sentiment_score', 0) for n in news_list]
        
        positive = sum(1 for s in scores if s > 0.2)
        negative = sum(1 for s in scores if s < -0.2)
        neutral = len(scores) - positive - negative
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        if avg_score > 0.2:
            sentiment = 'positive'
        elif avg_score < -0.2:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': avg_score,
            'positive_count': positive,
            'negative_count': negative,
            'neutral_count': neutral,
            'total_news': len(news_list)
        }
    
    def get_market_news(self, days: int = 1) -> List[dict]:
        """获取市场新闻"""
        try:
            import akshare as ak
            
            df = ak.stock_news_em(symbol="全球")
            
            news_list = []
            if df is not None and not df.empty:
                for _, row in df.head(20).iterrows():
                    news_list.append({
                        'title': row.get('新闻标题', ''),
                        'url': row.get('新闻链接', ''),
                        'datetime': str(row.get('发布时间', '')),
                        'source': row.get('文章来源', '')
                    })
            
            return news_list if news_list else self._generate_mock_market_news()
            
        except Exception as e:
            self.logger.warning(f"获取市场新闻失败: {e}")
            return self._generate_mock_market_news()
    
    def _generate_mock_market_news(self) -> List[dict]:
        """生成模拟市场新闻"""
        titles = [
            "A股市场今日震荡上行",
            "央行发布最新货币政策",
            "沪深两市成交额突破万亿元",
            "外资持续流入A股市场",
            "科创板再迎新股上市",
            "券商看好后市行情",
        ]
        
        return [
            {
                'title': random.choice(titles),
                'url': f"https://example.com/market/{i}",
                'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'source': random.choice(['证券时报', '上海证券报', '中国证券报'])
            }
            for i in range(10)
        ]
