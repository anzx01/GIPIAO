import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import loguru


class DataStorage:
    """数据存储管理器"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = loguru.logger
        
        self.price_dir = self.data_dir / "prices"
        self.financial_dir = self.data_dir / "financial"
        self.news_dir = self.data_dir / "news"
        
        for d in [self.price_dir, self.financial_dir, self.news_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def save_price_data(self, code: str, df: pd.DataFrame) -> str:
        """保存行情数据"""
        file_path = self.price_dir / f"{code}_{datetime.now().strftime('%Y%m%d')}.parquet"
        
        df.to_parquet(file_path, index=False)
        self.logger.info(f"保存 {code} 行情数据到 {file_path}")
        
        return str(file_path)
    
    def load_price_data(self, code: str, date: str = None) -> Optional[pd.DataFrame]:
        """加载行情数据"""
        if date:
            file_path = self.price_dir / f"{code}_{date}.parquet"
        else:
            files = list(self.price_dir.glob(f"{code}_*.parquet"))
            if not files:
                return None
            file_path = max(files, key=lambda x: x.stat().st_mtime)
        
        if file_path.exists():
            return pd.read_parquet(file_path)
        return None
    
    def load_all_price_data(self, code: str) -> pd.DataFrame:
        """加载所有历史行情数据"""
        files = list(self.price_dir.glob(f"{code}_*.parquet"))
        
        if not files:
            return pd.DataFrame()
        
        dfs = []
        for f in sorted(files):
            df = pd.read_parquet(f)
            dfs.append(df)
        
        if dfs:
            result = pd.concat(dfs, ignore_index=True)
            return result.sort_values('date').drop_duplicates(subset=['date'])
        return pd.DataFrame()
    
    def save_financial_data(self, code: str, data: dict) -> str:
        """保存财务数据"""
        file_path = self.financial_dir / f"{code}_financial.json"
        
        data['saved_at'] = datetime.now().isoformat()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"保存 {code} 财务数据")
        return str(file_path)
    
    def load_financial_data(self, code: str) -> Optional[dict]:
        """加载财务数据"""
        file_path = self.financial_dir / f"{code}_financial.json"
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def save_news(self, code: str, news_list: List[dict]) -> str:
        """保存新闻数据"""
        file_path = self.news_dir / f"{code}_news.json"
        
        data = {
            'code': code,
            'news': news_list,
            'saved_at': datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"保存 {code} {len(news_list)} 条新闻")
        return str(file_path)
    
    def load_news(self, code: str) -> List[dict]:
        """加载新闻数据"""
        file_path = self.news_dir / f"{code}_news.json"
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('news', [])
        return []
    
    def get_latest_data_date(self, code: str) -> Optional[str]:
        """获取最新数据日期"""
        files = list(self.price_dir.glob(f"{code}_*.parquet"))
        
        if not files:
            return None
        
        dates = [f.stem.split('_')[1] for f in files]
        return max(dates)
    
    def list_available_stocks(self) -> List[str]:
        """列出已有数据的股票"""
        files = list(self.price_dir.glob("*.parquet"))
        
        codes = set()
        for f in files:
            code = f.stem.rsplit('_', 1)[0]
            codes.add(code)
        
        return sorted(list(codes))
    
    def export_to_csv(self, code: str, output_dir: str = None) -> str:
        """导出数据到CSV"""
        df = self.load_all_price_data(code)
        
        if df.empty:
            return None
        
        if output_dir is None:
            output_dir = self.data_dir / "exports"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = output_dir / f"{code}_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        
        return str(file_path)
