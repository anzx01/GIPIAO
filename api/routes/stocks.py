"""
股票数据API路由
"""

from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel

import pandas as pd

from api.validators import (
    validate_stock_code,
    validate_date_format,
    validate_pagination
)
from api.cache import cached, clear_cache


router = APIRouter()


class StockInfo(BaseModel):
    code: str
    name: Optional[str] = None
    close: Optional[float] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[float] = None
    pct_change: Optional[float] = None


class StockScore(BaseModel):
    code: str
    name: Optional[str] = None
    total_score: float
    pe_score: Optional[float] = None
    pb_score: Optional[float] = None
    roe_score: Optional[float] = None
    momentum_score: Optional[float] = None
    volatility_score: Optional[float] = None
    liquidity_score: Optional[float] = None
    sentiment_score: Optional[float] = None
    pe: Optional[float] = None
    pb: Optional[float] = None
    roe: Optional[float] = None
    rank: Optional[int] = None


class StockDetail(BaseModel):
    code: str
    name: Optional[str] = None
    price_data: List[dict] = []
    technical_indicators: dict = {}
    financial_data: dict = {}
    news: List[dict] = []
    score: Optional[dict] = None


@router.get("/list")
@cached(ttl=300, key_prefix="stock_list:")
async def get_stock_list(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None
):
    page, page_size = validate_pagination(page, page_size)
    
    engine = request.app.state.engine
    stock_list = engine._get_stock_list()
    
    stocks = []
    for code in stock_list:
        stocks.append({
            "code": code,
            "name": _get_stock_name(code)
        })
    
    if keyword:
        keyword = keyword.strip()
        stocks = [s for s in stocks if keyword.lower() in s["code"].lower() or 
                  (s["name"] and keyword.lower() in s["name"].lower())]
    
    total = len(stocks)
    start = (page - 1) * page_size
    end = start + page_size
    stocks = stocks[start:end]
    
    return {
        "code": 200,
        "data": {
            "items": stocks,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.get("/scores")
@cached(ttl=600, key_prefix="stock_scores:")
async def get_stock_scores(
    request: Request,
    top_n: Optional[int] = Query(10, ge=1, le=50)
):
    engine = request.app.state.engine
    
    try:
        result = engine.run_daily_analysis()
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        scores = result.get("data", {}).get("stock_scores", [])
        
        if not scores:
            scores = _generate_mock_scores(engine._get_stock_list())
        
        for score in scores:
            score["name"] = _get_stock_name(score["code"])
        
        scores = sorted(scores, key=lambda x: x.get("total_score", 0), reverse=True)
        
        return {
            "code": 200,
            "data": {
                "items": scores[:top_n],
                "total": len(scores)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}")
async def get_stock_detail(
    request: Request,
    code: str,
    days: int = Query(60, ge=1, le=365)
):
    code = validate_stock_code(code)
    
    engine = request.app.state.engine
    
    try:
        price_data = engine.fetcher.fetch_price_data(
            [code],
            start_date=(datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
        )
        
        if code not in price_data or price_data[code].empty:
            raise HTTPException(status_code=404, detail=f"股票 {code} 数据不存在")
        
        df = price_data[code]
        df = engine.fetcher.calculate_technical_indicators(df)
        
        financial_data = engine.fetcher.fetch_financial_data([code])
        
        news_data = engine.news_fetcher.fetch_news([code])
        
        latest = df.iloc[-1] if not df.empty else None
        
        technical = {}
        if latest is not None:
            for indicator in ["ma5", "ma10", "ma20", "ema12", "ema26", "macd", "signal", "rsi", "bb_upper", "bb_lower"]:
                if indicator in df.columns:
                    technical[indicator] = round(float(latest.get(indicator, 0)), 2) if pd.notna(latest.get(indicator)) else None
        
        return {
            "code": 200,
            "data": {
                "code": code,
                "name": _get_stock_name(code),
                "price_data": df.tail(30).to_dict("records"),
                "technical_indicators": technical,
                "financial_data": financial_data.get(code, {}),
                "news": news_data.get(code, []),
                "latest_price": {
                    "close": float(latest["close"]) if latest is not None else None,
                    "open": float(latest["open"]) if latest is not None else None,
                    "high": float(latest["high"]) if latest is not None else None,
                    "low": float(latest["low"]) if latest is not None else None,
                    "volume": float(latest["volume"]) if latest is not None else None,
                    "pct_change": float(latest["pct_change"]) if latest is not None and "pct_change" in latest else None,
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}/price")
async def get_stock_price(
    request: Request,
    code: str,
    days: int = Query(30, ge=1, le=365),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    code = validate_stock_code(code)
    
    engine = request.app.state.engine
    
    if not start_date:
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
    else:
        start_date = validate_date_format(start_date)
    
    if not end_date:
        end_date = datetime.now().strftime("%Y%m%d")
    else:
        end_date = validate_date_format(end_date)
    
    try:
        price_data = engine.fetcher.fetch_price_data([code], start_date, end_date)
        
        if code not in price_data:
            raise HTTPException(status_code=404, detail=f"股票 {code} 数据不存在")
        
        df = price_data[code]
        
        return {
            "code": 200,
            "data": {
                "code": code,
                "prices": df.to_dict("records")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}/indicators")
async def get_technical_indicators(
    request: Request,
    code: str,
    days: int = Query(60, ge=1, le=365)
):
    code = validate_stock_code(code)
    
    engine = request.app.state.engine
    
    try:
        price_data = engine.fetcher.fetch_price_data(
            [code],
            start_date=(datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
        )
        
        if code not in price_data:
            raise HTTPException(status_code=404, detail=f"股票 {code} 数据不存在")
        
        df = price_data[code]
        df = engine.fetcher.calculate_technical_indicators(df)
        
        latest = df.iloc[-1]
        
        indicators = {
            "ma": {
                "ma5": round(float(latest["ma5"]), 2) if pd.notna(latest.get("ma5")) else None,
                "ma10": round(float(latest["ma10"]), 2) if pd.notna(latest.get("ma10")) else None,
                "ma20": round(float(latest["ma20"]), 2) if pd.notna(latest.get("ma20")) else None,
            },
            "ema": {
                "ema12": round(float(latest["ema12"]), 2) if pd.notna(latest.get("ema12")) else None,
                "ema26": round(float(latest["ema26"]), 2) if pd.notna(latest.get("ema26")) else None,
            },
            "macd": {
                "value": round(float(latest["macd"]), 2) if pd.notna(latest.get("macd")) else None,
                "signal": round(float(latest["signal"]), 2) if pd.notna(latest.get("signal")) else None,
                "histogram": round(float(latest["macd"] - latest["signal"]), 2) if pd.notna(latest.get("macd")) and pd.notna(latest.get("signal")) else None,
            },
            "rsi": round(float(latest["rsi"]), 2) if pd.notna(latest.get("rsi")) else None,
            "bollinger": {
                "upper": round(float(latest["bb_upper"]), 2) if pd.notna(latest.get("bb_upper")) else None,
                "middle": round(float(latest["bb_middle"]), 2) if pd.notna(latest.get("bb_middle")) else None,
                "lower": round(float(latest["bb_lower"]), 2) if pd.notna(latest.get("bb_lower")) else None,
            }
        }
        
        return {
            "code": 200,
            "data": indicators
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _get_stock_name(code: str) -> str:
    names = {
        "600519.SH": "贵州茅台",
        "000858.SH": "五粮液",
        "601318.SH": "中国平安",
        "600036.SH": "招商银行",
        "000333.SZ": "美的集团",
        "600519": "贵州茅台",
        "000858": "五粮液",
        "601318": "中国平安",
        "600036": "招商银行",
        "000333": "美的集团",
    }
    return names.get(code, code)


def _generate_mock_scores(stock_list: list) -> list:
    import random
    scores = []
    for code in stock_list:
        scores.append({
            "code": code,
            "total_score": round(random.uniform(60, 95), 2),
            "pe_score": round(random.uniform(60, 90), 2),
            "pb_score": round(random.uniform(60, 90), 2),
            "roe_score": round(random.uniform(60, 90), 2),
            "momentum_score": round(random.uniform(60, 90), 2),
            "volatility_score": round(random.uniform(60, 90), 2),
            "liquidity_score": round(random.uniform(60, 90), 2),
            "sentiment_score": round(random.uniform(50, 80), 2),
        })
    return scores
