"""
Backtest API routes.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel


router = APIRouter()


class BacktestRequest(BaseModel):
    portfolio: dict[str, float]
    start_date: str | None = None
    end_date: str | None = None
    initial_capital: float | None = 1000000


class CompareRequest(BaseModel):
    portfolios: list[dict[str, float]]
    start_date: str | None = None
    end_date: str | None = None


def _serialize_doc(doc: dict[str, Any]) -> dict[str, Any]:
    item = dict(doc)
    item.pop("_id", None)
    for field in ("created_at", "saved_at"):
        if hasattr(item.get(field), "isoformat"):
            item[field] = item[field].isoformat()
    return item


@router.post("/run")
async def run_backtest(request: Request, backtest: BacktestRequest):
    engine = request.app.state.engine

    try:
        result = engine.backtest_portfolio(
            portfolio=backtest.portfolio,
            start_date=backtest.start_date,
            end_date=backtest.end_date,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Real backtest unavailable: {exc}",
        ) from exc

    return {"code": 200, "data": result}


@router.get("/history")
async def get_backtest_history(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    sort_by: str = Query("created_at", description="Sort field: created_at, total_return, sharpe_ratio"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
):
    engine = request.app.state.engine

    if hasattr(engine.storage, "load_backtest_results"):
        history_data = engine.storage.load_backtest_results()
    elif hasattr(engine, "_get_backtest_history"):
        history_data = engine._get_backtest_history()
    else:
        history_data = []

    history_data = [_serialize_doc(item) for item in history_data]

    reverse = sort_order == "desc"
    history_data.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)

    total = len(history_data)
    start = (page - 1) * page_size
    end = start + page_size
    items = history_data[start:end]

    return {
        "code": 200,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }


@router.get("/{backtest_id}")
async def get_backtest_detail(request: Request, backtest_id: str):
    engine = request.app.state.engine

    if hasattr(engine, "_get_backtest_detail"):
        try:
            detail = engine._get_backtest_detail(backtest_id)
        except Exception as exc:
            raise HTTPException(status_code=404, detail="Backtest not found") from exc
        return {"code": 200, "data": _serialize_doc(detail)}

    if hasattr(engine.storage, "backtest_results"):
        doc = engine.storage.backtest_results.find_one({"id": backtest_id})
        if doc:
            return {"code": 200, "data": _serialize_doc(doc)}

    raise HTTPException(status_code=404, detail="Backtest not found")


@router.post("/compare")
async def compare_strategies(request: Request, compare: CompareRequest):
    engine = request.app.state.engine

    results = []
    for i, portfolio in enumerate(compare.portfolios):
        try:
            result = engine.backtest_portfolio(
                portfolio=portfolio,
                start_date=compare.start_date,
                end_date=compare.end_date,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Real backtest unavailable for strategy {i + 1}: {exc}",
            ) from exc

        result["name"] = f"策略{i + 1}"
        results.append(result)

    if not results:
        return {
            "code": 200,
            "data": {
                "results": [],
                "comparison": [],
                "metrics": {},
            },
        }

    comparison_df = engine.backtest.compare_strategies(results)
    comparison_data = comparison_df.to_dict("records") if not comparison_df.empty else []

    return {
        "code": 200,
        "data": {
            "results": results,
            "comparison": comparison_data,
            "metrics": {
                "best_return": max(results, key=lambda x: x.get("total_return", 0)),
                "best_sharpe": max(results, key=lambda x: x.get("sharpe_ratio", 0)),
                "lowest_drawdown": min(results, key=lambda x: x.get("max_drawdown", float("inf"))),
            },
        },
    }


@router.get("/optimize/weights")
async def optimize_portfolio_weights(
    request: Request,
    codes: str = Query(..., description="股票代码列表，逗号分隔"),
    method: str = Query("equal", description="优化方法: equal, risk_parity, max_sharpe"),
):
    engine = request.app.state.engine
    stock_list = [code.strip() for code in codes.split(",") if code.strip()]

    try:
        result = engine.optimize_portfolio(stock_list)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Real portfolio optimization unavailable: {exc}",
        ) from exc

    return {
        "code": 200,
        "data": {
            **result,
            "method": method,
        },
    }
