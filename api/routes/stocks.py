"""
股票数据API路由
"""

from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
from loguru import logger

import pandas as pd

from api.validators import (
    validate_stock_code,
    validate_date_format,
    validate_pagination
)
from api.cache import cached, clear_cache
from skills.skill_data.text_utils import repair_mojibake_text


router = APIRouter()


def _serialize_score(score: dict) -> dict:
    item = dict(score)
    for key, value in list(item.items()):
        if hasattr(value, "item"):
            item[key] = value.item()
        elif hasattr(value, "isoformat"):
            item[key] = value.isoformat()
    return item


def _generate_real_scores(engine, limit: int = 50) -> list[dict]:
    stock_list = engine._get_stock_list()
    if not stock_list:
        return []

    price_data = engine.fetcher.fetch_price_data(stock_list)
    if not price_data:
        return []

    for code, df in list(price_data.items()):
        if df is None or df.empty:
            price_data.pop(code, None)
            continue
        price_data[code] = engine.fetcher.calculate_technical_indicators(df)

    if not price_data:
        return []

    financial_data = engine.fetcher.fetch_financial_data(list(price_data.keys()))
    scores_df = engine.scorer.score_stocks(price_data, financial_data, {})
    if scores_df.empty:
        return []

    scores = [_serialize_score(row) for row in scores_df.head(limit).to_dict("records")]

    for score in scores:
        try:
            engine.storage.save_stock_score(score)
        except Exception as exc:
            logger.error(f"Failed to save stock score {score.get('code')}: {exc}")

    return scores


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
            "name": await _get_stock_name(request, code)
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
async def get_stock_scores(
    request: Request,
    top_n: Optional[int] = Query(10, ge=1, le=50)
):
    engine = request.app.state.engine

    try:
        # 先尝试从存储中读取已有的评分数据
        scores = engine.storage.load_latest_scores(limit=50)

        if not scores:
            scores = _generate_real_scores(engine, limit=50)
            if not scores:
                return {
                    "code": 200,
                    "data": {
                        "items": [],
                        "total": 0,
                        "message": "暂无真实评分数据，请检查行情数据源或股票池配置"
                    }
                }

        # 添加股票名称
        for score in scores:
            score["name"] = await _get_stock_name(request, score["code"])

        # 按评分排序
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
        logger.error(f"Error in get_stock_scores: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}")
async def get_stock_detail(
    request: Request,
    code: str,
    days: int = Query(60, ge=1, le=365)
):
    raw_code = code
    try:
        code = validate_stock_code(code)
    except HTTPException:
        raise HTTPException(status_code=404, detail=f"Stock {raw_code} not found")
    
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
        
        financial_data = {}
        try:
            financial_data = engine.fetcher.fetch_financial_data([code])
        except Exception as e:
            logger.error(f"Error fetching financial data: {e}")
        
        news_data = {}
        try:
            news_data = engine.news_fetcher.fetch_news([code])
        except Exception as e:
            logger.error(f"Error fetching news data: {e}")
        
        latest = df.iloc[-1] if not df.empty else None
        
        technical = {}
        if latest is not None:
            for indicator in ["ma5", "ma10", "ma20", "ema12", "ema26", "macd", "signal", "rsi", "bb_upper", "bb_lower"]:
                if indicator in df.columns:
                    val = latest[indicator] if indicator in latest.index else None
                    try:
                        technical[indicator] = round(float(val), 2) if pd.notna(val) else None
                    except (TypeError, ValueError):
                        technical[indicator] = None
        
        price_data_records = []
        try:
            df_copy = df.copy()
            df_copy['date'] = df_copy['date'].dt.strftime('%Y-%m-%d')
            df_copy = df_copy.replace({float('nan'): None})
            price_data_records = df_copy.tail(30).to_dict("records")
        except Exception as e:
            logger.error(f"Error converting price data to dict: {e}")
            price_data_records = []
        
        latest_price = {}
        if latest is not None:
            try:
                latest_price = {
                    "close": float(latest["close"]) if "close" in latest.index and pd.notna(latest["close"]) else None,
                    "open": float(latest["open"]) if "open" in latest.index and pd.notna(latest["open"]) else None,
                    "high": float(latest["high"]) if "high" in latest.index and pd.notna(latest["high"]) else None,
                    "low": float(latest["low"]) if "low" in latest.index and pd.notna(latest["low"]) else None,
                    "volume": float(latest["volume"]) if "volume" in latest.index and pd.notna(latest["volume"]) else None,
                    "pct_change": float(latest["pct_change"]) if "pct_change" in latest.index and pd.notna(latest["pct_change"]) else None,
                }
            except (TypeError, ValueError) as e:
                logger.error(f"Error converting latest price: {e}")
                latest_price = {}
        
        return {
            "code": 200,
            "data": {
                "code": code,
                "name": await _get_stock_name(request, code),
                "price_data": price_data_records,
                "technical_indicators": technical,
                "financial_data": financial_data.get(code, {}),
                "news": news_data.get(code, []),
                "latest_price": latest_price
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_stock_detail for {code}: {str(e)}", exc_info=True)
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


async def _get_stock_name(request: Request, code: str) -> str:
    engine = request.app.state.engine
    
    # 尝试从缓存的映射中获取
    if not hasattr(engine, 'stock_map') or not engine.stock_map:
        try:
            engine.stock_map = engine.fetcher.get_stock_info_map()
        except Exception as e:
            logger.error(f"Failed to fetch stock info map: {e}")
            engine.stock_map = {}
            
    if code in engine.stock_map:
        name = repair_mojibake_text(engine.stock_map[code])
        engine.stock_map[code] = name
        return name
        
    return code
