from pymongo import MongoClient
from pymongo.collection import Collection
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import os


class MongoDBStorage:
    def __init__(self, connection_string: str = None, database: str = "aiqrh"):
        self.connection_string = connection_string or os.getenv(
            "MONGO_CONNECTION",
            "mongodb://localhost:27017/aiqrh"
        )
        self.database_name = database
        self.client: Optional[MongoClient] = None
        self.db = None
        
    def connect(self):
        if self.client is None:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
        return self
    
    def close(self):
        if self.client:
            self.client.close()
            self.client = None
    
    @property
    def prices(self) -> Collection:
        return self.db["stock_prices"]
    
    @property
    def financials(self) -> Collection:
        return self.db["stock_financials"]
    
    @property
    def news(self) -> Collection:
        return self.db["stock_news"]
    
    @property
    def scores(self) -> Collection:
        return self.db["stock_scores"]
    
    @property
    def portfolios(self) -> Collection:
        return self.db["portfolios"]
    
    @property
    def backtest_results(self) -> Collection:
        return self.db["backtest_results"]
    
    def save_price_data(self, code: str, df: pd.DataFrame) -> int:
        records = df.to_dict('records')
        for r in records:
            r['stock_code'] = code
            r['saved_at'] = datetime.now()
            
        result = self.prices.update_many(
            {'stock_code': code},
            {'$set': {'deleted': True}},
            upsert=False
        )
        self.prices.delete_many({'stock_code': code, 'deleted': True})
        
        if records:
            self.prices.insert_many(records)
        return len(records)
    
    def load_price_data(self, code: str, start_date: str = None, 
                        end_date: str = None, limit: int = None) -> pd.DataFrame:
        query = {'stock_code': code}
        
        if start_date or end_date:
            query['date'] = {}
            if start_date:
                query['date']['$gte'] = start_date
            if end_date:
                query['date']['$lte'] = end_date
        
        cursor = self.prices.find(query).sort('date', 1)
        
        if limit:
            cursor = cursor.limit(limit)
        
        data = list(cursor)
        
        if data:
            for d in data:
                d.pop('_id', None)
                d.pop('saved_at', None)
            return pd.DataFrame(data)
        return pd.DataFrame()
    
    def save_financial_data(self, code: str, data: dict) -> str:
        data['stock_code'] = code
        data['saved_at'] = datetime.now()
        
        self.financials.update_one(
            {'stock_code': code},
            {'$set': data},
            upsert=True
        )
        return code
    
    def load_financial_data(self, code: str) -> Optional[dict]:
        result = self.financials.find_one({'stock_code': code})
        if result:
            result.pop('_id', None)
            result.pop('saved_at', None)
        return result
    
    def save_news(self, code: str, news_list: List[dict]) -> int:
        if not news_list:
            return 0
            
        self.news.delete_many({'stock_code': code})
        
        for n in news_list:
            n['stock_code'] = code
            n['saved_at'] = datetime.now()
        
        self.news.insert_many(news_list)
        return len(news_list)
    
    def load_news(self, code: str, limit: int = 50) -> List[dict]:
        cursor = self.news.find(
            {'stock_code': code}
        ).sort('publish_date', -1).limit(limit)
        
        results = []
        for doc in cursor:
            doc.pop('_id', None)
            doc.pop('saved_at', None)
            doc.pop('stock_code', None)
            results.append(doc)
        return results
    
    def save_stock_score(self, score: dict) -> str:
        score['saved_at'] = datetime.now()
        
        self.scores.update_one(
            {'code': score['code']},
            {'$set': score},
            upsert=True
        )
        return score['code']
    
    def load_latest_scores(self, limit: int = 10) -> List[dict]:
        cursor = self.scores.find().sort('total_score', -1).limit(limit)
        
        results = []
        for doc in cursor:
            doc.pop('_id', None)
            doc.pop('saved_at', None)
            results.append(doc)
        return results
    
    def save_portfolio(self, portfolio: dict) -> str:
        portfolio['updated_at'] = datetime.now()
        
        if '_id' in portfolio:
            portfolio.pop('_id')
            
        result = self.portfolios.update_one(
            {'name': portfolio['name']},
            {'$set': portfolio},
            upsert=True
        )
        
        return portfolio['name']
    
    def load_portfolios(self) -> List[dict]:
        cursor = self.portfolios.find()
        
        results = []
        for doc in cursor:
            doc.pop('_id', None)
            results.append(doc)
        return results
    
    def save_backtest_result(self, result: dict) -> str:
        result['saved_at'] = datetime.now()
        
        if '_id' in result:
            result.pop('_id')
            
        result_id = self.backtest_results.insert_one(result).inserted_id
        return str(result_id)
    
    def load_backtest_results(self, portfolio_id: str = None) -> List[dict]:
        query = {}
        if portfolio_id:
            query['portfolio_id'] = portfolio_id
            
        cursor = self.backtest_results.find(query).sort('saved_at', -1)
        
        results = []
        for doc in cursor:
            doc.pop('_id', None)
            results.append(doc)
        return results
