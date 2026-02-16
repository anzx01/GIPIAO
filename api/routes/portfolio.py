"""
组合管理API路由
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request, Body
from pydantic import BaseModel
from datetime import datetime


router = APIRouter()


class PortfolioCreate(BaseModel):
    name: str
    stocks: dict


class PortfolioUpdate(BaseModel):
    stocks: dict


@router.get("/list")
async def get_portfolio_list(request: Request):
    try:
        portfolios = [
            {
                "id": "1",
                "name": "默认组合",
                "stocks": {
                    "600519.SH": 0.3,
                    "000858.SH": 0.3,
                    "601318.SH": 0.2,
                    "600036.SH": 0.2
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        
        return {
            "code": 200,
            "data": {
                "items": portfolios,
                "total": len(portfolios)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{portfolio_id}")
async def get_portfolio_detail(request: Request, portfolio_id: str):
    engine = request.app.state.engine
    
    portfolios = {
        "1": {
            "id": "1",
            "name": "默认组合",
            "stocks": {
                "600519.SH": 0.3,
                "000858.SH": 0.3,
                "601318.SH": 0.2,
                "600036.SH": 0.2
            }
        }
    }
    
    portfolio = portfolios.get(portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="组合不存在")
    
    stock_list = list(portfolio["stocks"].keys())
    price_data = engine.fetcher.fetch_price_data(stock_list)
    
    current_prices = {}
    for code in stock_list:
        if code in price_data and not price_data[code].empty:
            current_prices[code] = float(price_data[code].iloc[-1]["close"])
    
    total_value = sum(
        weight * current_prices.get(code, 0)
        for code, weight in portfolio["stocks"].items()
    )
    
    return {
        "code": 200,
        "data": {
            **portfolio,
            "current_prices": current_prices,
            "total_value": total_value,
            "positions": [
                {
                    "code": code,
                    "weight": weight,
                    "price": current_prices.get(code, 0),
                    "value": weight * total_value
                }
                for code, weight in portfolio["stocks"].items()
            ]
        }
    }


@router.post("/")
async def create_portfolio(request: Request, portfolio: PortfolioCreate):
    return {
        "code": 200,
        "message": "组合创建成功",
        "data": {
            "id": "new_portfolio_id",
            "name": portfolio.name,
            "stocks": portfolio.stocks,
            "created_at": datetime.now().isoformat()
        }
    }


@router.put("/{portfolio_id}")
async def update_portfolio(
    request: Request,
    portfolio_id: str,
    portfolio: PortfolioUpdate
):
    return {
        "code": 200,
        "message": "组合更新成功",
        "data": {
            "id": portfolio_id,
            "stocks": portfolio.stocks,
            "updated_at": datetime.now().isoformat()
        }
    }


@router.delete("/{portfolio_id}")
async def delete_portfolio(request: Request, portfolio_id: str):
    return {
        "code": 200,
        "message": "组合删除成功"
    }


@router.get("/{portfolio_id}/performance")
async def get_portfolio_performance(
    request: Request,
    portfolio_id: str,
    days: int = 30
):
    return {
        "code": 200,
        "data": {
            "portfolio_id": portfolio_id,
            "days": days,
            "total_return": 5.23,
            "annual_return": 12.5,
            "daily_returns": [
                {"date": "2024-01-01", "return": 0.5},
                {"date": "2024-01-02", "return": -0.2},
            ]
        }
    }
