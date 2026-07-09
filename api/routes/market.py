"""
Market data API routes.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request, status


router = APIRouter()


def _iso_timestamp(value: Any) -> str:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if value:
        return str(value)
    return datetime.now().isoformat()


def _empty_collection(message: str, **extra: Any) -> dict:
    return {
        "code": 200,
        "data": {
            **extra,
            "items": [],
            "total": 0,
            "message": message,
        },
    }


def _stock_pool_summary(engine) -> dict | None:
    stock_list = engine._get_stock_list()
    if not stock_list:
        return None

    price_data = engine.fetcher.fetch_price_data(stock_list)
    rows = []
    for code, df in price_data.items():
        if df is None or df.empty:
            continue

        latest = df.iloc[-1]
        pct_change = latest.get("pct_change")
        if pct_change is None and len(df) >= 2 and "close" in df.columns:
            previous_close = df.iloc[-2].get("close")
            current_close = latest.get("close")
            if previous_close:
                pct_change = (current_close - previous_close) / previous_close * 100

        rows.append(
            {
                "code": code,
                "pct_change": float(pct_change or 0),
                "volume": float(latest.get("volume", 0) or 0),
                "amount": float(latest.get("amount", 0) or 0),
            }
        )

    if not rows:
        return None

    up_count = sum(1 for row in rows if row["pct_change"] > 0)
    down_count = sum(1 for row in rows if row["pct_change"] < 0)
    flat_count = len(rows) - up_count - down_count

    return {
        "total_stocks": len(rows),
        "up_count": up_count,
        "down_count": down_count,
        "flat_count": flat_count,
        "total_volume": sum(row["volume"] for row in rows),
        "total_amount": sum(row["amount"] for row in rows),
        "timestamp": datetime.now(),
        "scope": "stock_pool",
    }


@router.get("/summary")
async def get_market_summary(request: Request):
    engine = request.app.state.engine

    scope = "market"
    try:
        summary = engine.fetcher.fetch_market_summary()
    except Exception:
        summary = _stock_pool_summary(engine)
        scope = "stock_pool"
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Real market summary unavailable",
            )

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Real market summary unavailable",
        )

    total_stocks = int(summary.get("total_stocks") or 0)
    up_count = int(summary.get("up_count") or 0)

    return {
        "code": 200,
        "data": {
            "total_stocks": total_stocks,
            "up_count": up_count,
            "down_count": int(summary.get("down_count") or 0),
            "flat_count": int(summary.get("flat_count") or 0),
            "total_volume": float(summary.get("total_volume") or 0),
            "total_amount": float(summary.get("total_amount") or 0),
            "up_rate": round(up_count / total_stocks * 100, 2) if total_stocks else 0,
            "timestamp": _iso_timestamp(summary.get("timestamp")),
            "scope": summary.get("scope", scope),
        },
    }


@router.get("/indices")
async def get_market_indices(request: Request):
    fetch_index_data = getattr(request.app.state.engine.fetcher, "fetch_index_data", None)
    if not callable(fetch_index_data):
        return _empty_collection("Real index data source is not configured")

    try:
        indices = fetch_index_data()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Real index data unavailable: {exc}",
        ) from exc

    if isinstance(indices, dict):
        items = indices.get("items", [])
    else:
        items = indices or []

    return {"code": 200, "data": {"items": items, "total": len(items)}}


@router.get("/indices/{code}")
async def get_index_detail(request: Request, code: str):
    fetch_index_history = getattr(request.app.state.engine.fetcher, "fetch_index_history", None)
    if not callable(fetch_index_history):
        return {
            "code": 200,
            "data": {
                "code": code,
                "history": [],
                "message": "Real index history source is not configured",
            },
        }

    try:
        history = fetch_index_history(code, days=30)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Real index history unavailable: {exc}",
        ) from exc

    return {"code": 200, "data": {"code": code, "history": history or []}}


@router.get("/industry/heat")
async def get_industry_heat(request: Request):
    fetch_industry_data = getattr(request.app.state.engine.fetcher, "fetch_industry_data", None)
    if not callable(fetch_industry_data):
        return _empty_collection("Real industry heat source is not configured")

    try:
        industries = fetch_industry_data()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Real industry heat data unavailable: {exc}",
        ) from exc

    return {
        "code": 200,
        "data": {
            "items": industries or [],
            "total": len(industries or []),
        },
    }


@router.get("/industry/{code}")
async def get_industry_detail(request: Request, code: str, days: int = Query(30, ge=1, le=90)):
    fetch_industry_stocks = getattr(request.app.state.engine.fetcher, "fetch_industry_stocks", None)
    fetch_industry_history = getattr(request.app.state.engine.fetcher, "fetch_industry_history", None)
    if not callable(fetch_industry_stocks) or not callable(fetch_industry_history):
        return {
            "code": 200,
            "data": {
                "code": code,
                "stocks": [],
                "history": [],
                "message": "Real industry detail source is not configured",
            },
        }

    try:
        stocks = fetch_industry_stocks(code)
        history = fetch_industry_history(code, days=days)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Real industry detail unavailable: {exc}",
        ) from exc

    return {
        "code": 200,
        "data": {
            "code": code,
            "stocks": (stocks or [])[:20],
            "history": history or [],
        },
    }


@router.get("/sector/performance")
async def get_sector_performance(request: Request, days: int = Query(5, ge=1, le=30)):
    fetch_sector_data = getattr(request.app.state.engine.fetcher, "fetch_sector_data", None)
    if not callable(fetch_sector_data):
        return _empty_collection(
            "Real sector performance source is not configured",
            days=days,
        )

    try:
        sectors = fetch_sector_data()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Real sector performance unavailable: {exc}",
        ) from exc

    return {
        "code": 200,
        "data": {
            "days": days,
            "sectors": sectors or [],
        },
    }


@router.get("/sector/{code}")
async def get_sector_detail(request: Request, code: str, days: int = Query(30, ge=1, le=90)):
    fetch_sector_stocks = getattr(request.app.state.engine.fetcher, "fetch_sector_stocks", None)
    fetch_sector_history = getattr(request.app.state.engine.fetcher, "fetch_sector_history", None)
    if not callable(fetch_sector_stocks) or not callable(fetch_sector_history):
        return {
            "code": 200,
            "data": {
                "code": code,
                "stocks": [],
                "history": [],
                "message": "Real sector detail source is not configured",
            },
        }

    try:
        stocks = fetch_sector_stocks(code)
        history = fetch_sector_history(code, days=days)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Real sector detail unavailable: {exc}",
        ) from exc

    return {
        "code": 200,
        "data": {
            "code": code,
            "stocks": (stocks or [])[:20],
            "history": history or [],
        },
    }


@router.get("/turnover/rank")
async def get_turnover_rank(request: Request, limit: int = Query(10, ge=1, le=50)):
    engine = request.app.state.engine

    stock_list = engine._get_stock_list()
    price_data = engine.fetcher.fetch_price_data(stock_list)

    ranks = []
    for code, df in price_data.items():
        if df.empty:
            continue

        latest = df.iloc[-1]
        avg_volume = df.tail(20)["volume"].mean() if "volume" in df.columns else 0
        ranks.append(
            {
                "code": code,
                "volume": float(latest.get("volume", 0)),
                "avg_volume_20d": float(avg_volume),
                "turnover": float(latest.get("turnover", 0)),
            }
        )

    ranks.sort(key=lambda x: x["volume"], reverse=True)

    return {
        "code": 200,
        "data": {
            "items": ranks[:limit],
            "total": len(ranks),
        },
    }
