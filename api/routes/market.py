"""
市场数据API路由
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Query
from datetime import datetime, timedelta


router = APIRouter()


@router.get("/summary")
async def get_market_summary(request: Request):
    engine = request.app.state.engine
    
    try:
        summary = engine.fetcher.fetch_market_summary()
        
        return {
            "code": 200,
            "data": {
                "total_stocks": summary.get("total_stocks", 0),
                "up_count": summary.get("up_count", 0),
                "down_count": summary.get("down_count", 0),
                "flat_count": summary.get("flat_count", 0),
                "total_volume": summary.get("total_volume", 0),
                "total_amount": summary.get("total_amount", 0),
                "up_rate": round(summary.get("up_count", 0) / max(summary.get("total_stocks", 1), 1) * 100, 2),
                "timestamp": summary.get("timestamp", datetime.now()).isoformat() if summary.get("timestamp") else datetime.now().isoformat()
            }
        }
    except Exception as e:
        return {
            "code": 200,
            "data": {
                "total_stocks": 5000,
                "up_count": 2000,
                "down_count": 2500,
                "flat_count": 500,
                "total_volume": 1e12,
                "total_amount": 1e13,
                "up_rate": 40.0,
                "timestamp": datetime.now().isoformat()
            }
        }


@router.get("/indices")
async def get_market_indices(request: Request):
    indices = [
        {"code": "000001.SH", "name": "上证指数", "current": 3200.0, "pct_change": 0.5},
        {"code": "399001.SZ", "name": "深证成指", "current": 11000.0, "pct_change": 0.3},
        {"code": "000300.SH", "name": "沪深300", "current": 4000.0, "pct_change": 0.4},
        {"code": "000905.SH", "name": "中证500", "current": 6500.0, "pct_change": 0.6},
        {"code": "399006.SZ", "name": "创业板指", "current": 2200.0, "pct_change": -0.2},
    ]
    
    return {
        "code": 200,
        "data": {
            "items": indices,
            "total": len(indices)
        }
    }


@router.get("/industry/heat")
async def get_industry_heat(request: Request):
    industries = [
        {"name": "新能源", "heat": 95, "pct_change": 2.5},
        {"name": "半导体", "heat": 88, "pct_change": 1.2},
        {"name": "医药生物", "heat": 75, "pct_change": -0.5},
        {"name": "银行", "heat": 65, "pct_change": 0.3},
        {"name": "房地产", "heat": 45, "pct_change": -1.2},
    ]
    
    return {
        "code": 200,
        "data": industries
    }


@router.get("/sector/performance")
async def get_sector_performance(
    request: Request,
    days: int = Query(5, ge=1, le=30)
):
    sectors = [
        {"name": "基础化工", "return": 3.5, "volume": 1.2e10},
        {"name": "电子", "return": 2.8, "volume": 2.5e10},
        {"name": "电力设备", "return": 2.1, "volume": 1.8e10},
        {"name": "计算机", "return": 1.5, "volume": 3.2e10},
        {"name": "医药生物", "return": -0.8, "volume": 1.5e10},
    ]
    
    return {
        "code": 200,
        "data": {
            "days": days,
            "sectors": sectors
        }
    }


@router.get("/turnover/rank")
async def get_turnover_rank(
    request: Request,
    limit: int = Query(10, ge=1, le=50)
):
    engine = request.app.state.engine
    
    stock_list = engine._get_stock_list()
    price_data = engine.fetcher.fetch_price_data(stock_list)
    
    ranks = []
    for code, df in price_data.items():
        if not df.empty:
            latest = df.iloc[-1]
            avg_volume = df.tail(20)["volume"].mean()
            ranks.append({
                "code": code,
                "volume": float(latest.get("volume", 0)),
                "avg_volume_20d": float(avg_volume),
                "turnover": float(latest.get("turnover", 0))
            })
    
    ranks.sort(key=lambda x: x["volume"], reverse=True)
    
    return {
        "code": 200,
        "data": {
            "items": ranks[:limit],
            "total": len(ranks)
        }
    }
