"""
回测API路由
"""

from typing import Optional, Dict, List
from fastapi import APIRouter, HTTPException, Request, Query, Body
from pydantic import BaseModel
from datetime import datetime


router = APIRouter()


class BacktestRequest(BaseModel):
    portfolio: Dict[str, float]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    initial_capital: Optional[float] = 1000000


class CompareRequest(BaseModel):
    portfolios: List[Dict[str, float]]
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@router.post("/run")
async def run_backtest(request: Request, backtest: BacktestRequest):
    engine = request.app.state.engine
    
    try:
        result = engine.backtest_portfolio(
            portfolio=backtest.portfolio,
            start_date=backtest.start_date,
            end_date=backtest.end_date
        )
        
        return {
            "code": 200,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_backtest_history(request: Request):
    return {
        "code": 200,
        "data": {
            "items": [
                {
                    "id": "1",
                    "name": "测试回测",
                    "portfolio": {"600519.SH": 0.5, "000858.SH": 0.5},
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31",
                    "total_return": 15.5,
                    "sharpe_ratio": 1.2,
                    "max_drawdown": 8.5,
                    "created_at": "2024-01-01T00:00:00"
                }
            ],
            "total": 1
        }
    }


@router.get("/{backtest_id}")
async def get_backtest_detail(request: Request, backtest_id: str):
    return {
        "code": 200,
        "data": {
            "id": backtest_id,
            "name": "测试回测",
            "portfolio": {"600519.SH": 0.5, "000858.SH": 0.5},
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "initial_capital": 1000000,
            "final_value": 1155000,
            "total_return": 15.5,
            "annual_return": 15.5,
            "sharpe_ratio": 1.2,
            "max_drawdown": 8.5,
            "volatility": 12.3,
            "win_rate": 55.0,
            "portfolio_values": [
                {"date": "2023-01-01", "value": 1000000},
                {"date": "2023-12-31", "value": 1155000}
            ]
        }
    }


@router.post("/compare")
async def compare_strategies(request: Request, compare: CompareRequest):
    engine = request.app.state.engine
    
    results = []
    for i, portfolio in enumerate(compare.portfolios):
        try:
            result = engine.backtest_portfolio(
                portfolio=portfolio,
                start_date=compare.start_date,
                end_date=compare.end_date
            )
            result["name"] = f"策略{i+1}"
            results.append(result)
        except Exception as e:
            results.append({"name": f"策略{i+1}", "error": str(e)})
    
    comparison_df = engine.backtest.compare_strategies(results)
    
    return {
        "code": 200,
        "data": {
            "results": results,
            "comparison": comparison_df.to_dict('records') if not comparison_df.empty else []
        }
    }


@router.get("/optimize/weights")
async def optimize_portfolio_weights(
    request: Request,
    codes: str = Query(..., description="股票代码列表，逗号分隔"),
    method: str = Query("equal", description="优化方法: equal, risk_parity, max_sharpe")
):
    engine = request.app.state.engine
    
    stock_list = [c.strip() for c in codes.split(",")]
    
    try:
        result = engine.optimize_portfolio(stock_list)
        
        return {
            "code": 200,
            "data": result
        }
    except Exception as e:
        weights = {code: 1.0/len(stock_list) for code in stock_list}
        return {
            "code": 200,
            "data": {
                "weights": weights,
                "method": method,
                "note": "使用等权重分配"
            }
        }
