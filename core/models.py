from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class StockBase(BaseModel):
    code: str = Field(..., description="股票代码")
    name: Optional[str] = Field(None, description="股票名称")


class StockPrice(StockBase):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float
    pct_change: Optional[float] = 0
    turnover: Optional[float] = 0
    
    class Config:
        from_attributes = True


class StockFinancial(BaseModel):
    code: str
    date: datetime
    revenue: Optional[float] = None
    profit: Optional[float] = None
    roe: Optional[float] = None
    pe: Optional[float] = None
    pb: Optional[float] = None
    ps: Optional[float] = None
    market_cap: Optional[float] = None
    source: str = "akshare"


class StockScore(BaseModel):
    code: str
    total_score: float
    pe_score: float
    pb_score: float
    roe_score: float
    momentum_score: float
    volatility_score: float
    liquidity_score: float
    sentiment_score: Optional[float] = 50
    pe: Optional[float] = None
    pb: Optional[float] = None
    roe: Optional[float] = None
    market_cap: Optional[float] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


class Portfolio(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., description="组合名称")
    stocks: Dict[str, float] = Field(..., description="股票代码及权重")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True


class BacktestResult(BaseModel):
    id: Optional[str] = None
    portfolio_id: Optional[str] = None
    start_date: str
    end_date: str
    initial_capital: float
    final_value: float
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: Optional[float] = 0
    calmar_ratio: Optional[float] = 0
    volatility: float
    win_rate: float
    trading_days: int
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True


class NewsItem(BaseModel):
    code: str
    title: str
    content: Optional[str] = None
    source: str
    publish_date: datetime
    sentiment_score: Optional[float] = 0
    url: Optional[str] = None
    
    class Config:
        from_attributes = True


class MarketSummary(BaseModel):
    date: datetime
    total_stocks: int
    up_count: int
    down_count: int
    flat_count: int
    total_volume: float
    total_amount: float
    
    class Config:
        from_attributes = True


class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: Optional[str] = None
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True


class UserInDB(User):
    hashed_password: str


class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
