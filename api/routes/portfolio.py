"""
Portfolio management API routes.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel


router = APIRouter()


class PortfolioCreate(BaseModel):
    name: str
    stocks: dict[str, float]


class PortfolioUpdate(BaseModel):
    stocks: dict[str, float]


def _storage(request: Request):
    return request.app.state.engine.storage


def _portfolio_id(portfolio: dict[str, Any]) -> str | None:
    raw_id = portfolio.get("id") or portfolio.get("_id") or portfolio.get("name")
    return str(raw_id) if raw_id is not None else None


def _serialize_portfolio(portfolio: dict[str, Any]) -> dict[str, Any]:
    item = dict(portfolio)
    item.pop("_id", None)
    item["id"] = _portfolio_id(portfolio)
    for field in ("created_at", "updated_at", "saved_at"):
        if hasattr(item.get(field), "isoformat"):
            item[field] = item[field].isoformat()
    return item


def _load_portfolios(request: Request) -> list[dict[str, Any]]:
    storage = _storage(request)
    if not hasattr(storage, "load_portfolios"):
        return []

    portfolios = storage.load_portfolios()
    return [_serialize_portfolio(item) for item in portfolios]


def _find_portfolio(request: Request, portfolio_id: str) -> dict[str, Any] | None:
    for portfolio in _load_portfolios(request):
        if portfolio.get("id") == portfolio_id or portfolio.get("name") == portfolio_id:
            return portfolio
    return None


@router.get("/list")
async def get_portfolio_list(request: Request):
    portfolios = _load_portfolios(request)
    return {
        "code": 200,
        "data": {
            "items": portfolios,
            "total": len(portfolios),
        },
    }


@router.get("/{portfolio_id}")
async def get_portfolio_detail(request: Request, portfolio_id: str):
    portfolio = _find_portfolio(request, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    engine = request.app.state.engine
    stock_list = list((portfolio.get("stocks") or {}).keys())
    price_data = engine.fetcher.fetch_price_data(stock_list)

    current_prices = {}
    for code in stock_list:
        df = price_data.get(code)
        if df is not None and not df.empty and "close" in df.columns:
            current_prices[code] = float(df.iloc[-1]["close"])

    positions = []
    for code, weight in (portfolio.get("stocks") or {}).items():
        price = current_prices.get(code)
        positions.append(
            {
                "code": code,
                "weight": weight,
                "price": price,
            }
        )

    return {
        "code": 200,
        "data": {
            **portfolio,
            "current_prices": current_prices,
            "positions": positions,
        },
    }


@router.post("/")
async def create_portfolio(request: Request, portfolio: PortfolioCreate):
    storage = _storage(request)
    if not hasattr(storage, "save_portfolio"):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Portfolio storage is not configured",
        )

    payload = {
        "id": portfolio.name,
        "name": portfolio.name,
        "stocks": portfolio.stocks,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    storage.save_portfolio(payload)

    return {
        "code": 200,
        "message": "Portfolio created",
        "data": _serialize_portfolio(payload),
    }


@router.put("/{portfolio_id}")
async def update_portfolio(request: Request, portfolio_id: str, portfolio: PortfolioUpdate):
    storage = _storage(request)
    existing = _find_portfolio(request, portfolio_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    if not hasattr(storage, "save_portfolio"):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Portfolio storage is not configured",
        )

    payload = {
        **existing,
        "stocks": portfolio.stocks,
        "updated_at": datetime.now(),
    }
    storage.save_portfolio(payload)

    return {
        "code": 200,
        "message": "Portfolio updated",
        "data": _serialize_portfolio(payload),
    }


@router.delete("/{portfolio_id}")
async def delete_portfolio(request: Request, portfolio_id: str):
    storage = _storage(request)
    if not hasattr(storage, "portfolios"):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Portfolio storage is not configured",
        )

    result = storage.portfolios.delete_one({"$or": [{"id": portfolio_id}, {"name": portfolio_id}]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    return {"code": 200, "message": "Portfolio deleted"}


@router.get("/{portfolio_id}/performance")
async def get_portfolio_performance(request: Request, portfolio_id: str, days: int = 30):
    portfolio = _find_portfolio(request, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    stocks = portfolio.get("stocks") or {}
    if not stocks:
        raise HTTPException(status_code=400, detail="Portfolio has no stocks")

    try:
        result = request.app.state.engine.backtest_portfolio(stocks)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Real portfolio performance unavailable: {exc}",
        ) from exc

    return {
        "code": 200,
        "data": {
            "portfolio_id": portfolio_id,
            "days": days,
            **result,
        },
    }
