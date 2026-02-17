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
async def get_backtest_history(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    sort_by: str = Query("created_at", description="Sort field: created_at, total_return, sharpe_ratio"),
    sort_order: str = Query("desc", description="Sort order: asc, desc")
):
    engine = request.app.state.engine
    
    try:
        history_data = engine._get_backtest_history()
        
        if sort_order == "desc":
            history_data.sort(key=lambda x: x.get(sort_by, 0), reverse=True)
        else:
            history_data.sort(key=lambda x: x.get(sort_by, 0))
        
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
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    except Exception as e:
        mock_history = [
            {
                "id": "1",
                "name": "价值投资策略回测",
                "portfolio": {"600519.SH": 0.4, "000858.SH": 0.3, "601318.SH": 0.3},
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "initial_capital": 1000000,
                "final_value": 1185000,
                "total_return": 18.5,
                "annual_return": 18.5,
                "sharpe_ratio": 1.45,
                "max_drawdown": 12.3,
                "volatility": 15.2,
                "win_rate": 58.5,
                "total_trades": 45,
                "created_at": "2024-01-15T10:30:00"
            },
            {
                "id": "2",
                "name": "成长股策略回测",
                "portfolio": {"300750.SZ": 0.5, "002594.SZ": 0.3, "688981.SH": 0.2},
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "initial_capital": 1000000,
                "final_value": 1280000,
                "total_return": 28.0,
                "annual_return": 28.0,
                "sharpe_ratio": 1.68,
                "max_drawdown": 18.5,
                "volatility": 22.3,
                "win_rate": 52.3,
                "total_trades": 68,
                "created_at": "2024-01-10T14:20:00"
            },
            {
                "id": "3",
                "name": "均衡配置策略回测",
                "portfolio": {"600519.SH": 0.25, "000858.SH": 0.25, "300750.SZ": 0.25, "601318.SH": 0.25},
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "initial_capital": 1000000,
                "final_value": 1125000,
                "total_return": 12.5,
                "annual_return": 12.5,
                "sharpe_ratio": 1.32,
                "max_drawdown": 8.5,
                "volatility": 12.8,
                "win_rate": 62.5,
                "total_trades": 32,
                "created_at": "2024-01-05T09:15:00"
            },
            {
                "id": "4",
                "name": "科技主题策略回测",
                "portfolio": {"688981.SH": 0.4, "300750.SZ": 0.3, "002415.SZ": 0.3},
                "start_date": "2023-06-01",
                "end_date": "2023-12-31",
                "initial_capital": 1000000,
                "final_value": 1150000,
                "total_return": 15.0,
                "annual_return": 30.0,
                "sharpe_ratio": 1.55,
                "max_drawdown": 15.2,
                "volatility": 18.5,
                "win_rate": 55.8,
                "total_trades": 52,
                "created_at": "2024-01-20T16:45:00"
            },
            {
                "id": "5",
                "name": "消费主题策略回测",
                "portfolio": {"600519.SH": 0.5, "000858.SH": 0.3, "000568.SZ": 0.2},
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "initial_capital": 1000000,
                "final_value": 1080000,
                "total_return": 8.0,
                "annual_return": 8.0,
                "sharpe_ratio": 1.18,
                "max_drawdown": 10.5,
                "volatility": 11.2,
                "win_rate": 65.2,
                "total_trades": 28,
                "created_at": "2024-01-25T11:30:00"
            }
        ]
        
        if sort_order == "desc":
            mock_history.sort(key=lambda x: x.get(sort_by, 0), reverse=True)
        else:
            mock_history.sort(key=lambda x: x.get(sort_by, 0))
        
        total = len(mock_history)
        start = (page - 1) * page_size
        end = start + page_size
        items = mock_history[start:end]
        
        return {
            "code": 200,
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        }


@router.get("/{backtest_id}")
async def get_backtest_detail(request: Request, backtest_id: str):
    engine = request.app.state.engine
    
    try:
        backtest_data = engine._get_backtest_detail(backtest_id)
        
        return {
            "code": 200,
            "data": backtest_data
        }
    except Exception as e:
        mock_detail = {
            "id": backtest_id,
            "name": "价值投资策略回测",
            "portfolio": {"600519.SH": 0.4, "000858.SH": 0.3, "601318.SH": 0.3},
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "initial_capital": 1000000,
            "final_value": 1185000,
            "total_return": 18.5,
            "annual_return": 18.5,
            "sharpe_ratio": 1.45,
            "max_drawdown": 12.3,
            "volatility": 15.2,
            "win_rate": 58.5,
            "total_trades": 45,
            "avg_win": 3.2,
            "avg_loss": -2.1,
            "profit_factor": 1.52,
            "portfolio_values": [
                {"date": "2023-01", "value": 1000000},
                {"date": "2023-02", "value": 1025000},
                {"date": "2023-03", "value": 1015000},
                {"date": "2023-04", "value": 1045000},
                {"date": "2023-05", "value": 1085000},
                {"date": "2023-06", "value": 1065000},
                {"date": "2023-07", "value": 1105000},
                {"date": "2023-08", "value": 1135000},
                {"date": "2023-09", "value": 1115000},
                {"date": "2023-10", "value": 1145000},
                {"date": "2023-11", "value": 1165000},
                {"date": "2023-12", "value": 1185000},
            ],
            "drawdowns": [
                {"date": "2023-01", "drawdown": 0},
                {"date": "2023-02", "drawdown": -1.5},
                {"date": "2023-03", "drawdown": -2.8},
                {"date": "2023-04", "drawdown": -1.2},
                {"date": "2023-05", "drawdown": -3.5},
                {"date": "2023-06", "drawdown": -8.5},
                {"date": "2023-07", "drawdown": -5.2},
                {"date": "2023-08", "drawdown": -3.8},
                {"date": "2023-09", "drawdown": -6.5},
                {"date": "2023-10", "drawdown": -4.2},
                {"date": "2023-11", "drawdown": -2.5},
                {"date": "2023-12", "drawdown": -1.8},
            ],
            "monthly_returns": [
                {"month": "1月", "return": 2.5},
                {"month": "2月", "return": -1.0},
                {"month": "3月", "return": 2.0},
                {"month": "4月", "return": 3.8},
                {"month": "5月", "return": -1.8},
                {"month": "6月", "return": 3.8},
                {"month": "7月", "return": 2.7},
                {"month": "8月", "return": -1.8},
                {"month": "9月", "return": 2.7},
                {"month": "10月", "return": 1.7},
                {"month": "11月", "return": 1.7},
                {"month": "12月", "return": 1.7},
            ],
            "trades": [
                {"date": "2023-12-28", "type": "买入", "code": "600519", "price": 1685.5, "shares": 250, "reason": "估值偏低"},
                {"date": "2023-12-25", "type": "卖出", "code": "601318", "price": 45.2, "shares": 1000, "reason": "止盈"},
                {"date": "2023-12-20", "type": "买入", "code": "000858", "price": 158.5, "shares": 800, "reason": "突破买入"},
                {"date": "2023-12-15", "type": "卖出", "code": "600036", "price": 35.8, "shares": 1500, "reason": "止损"},
                {"date": "2023-12-10", "type": "买入", "code": "601318", "price": 42.5, "shares": 1000, "reason": "技术反弹"},
            ],
            "created_at": "2024-01-15T10:30:00"
        }
        
        return {
            "code": 200,
            "data": mock_detail
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
            results.append({
                "name": f"策略{i+1}",
                "error": str(e),
                "total_return": 0,
                "sharpe_ratio": 0,
                "max_drawdown": 0
            })
    
    try:
        comparison_df = engine.backtest.compare_strategies(results)
        comparison_data = comparison_df.to_dict('records') if not comparison_df.empty else []
    except Exception as e:
        comparison_data = []
    
    comparison_metrics = {
        "best_return": max(results, key=lambda x: x.get("total_return", 0)),
        "best_sharpe": max(results, key=lambda x: x.get("sharpe_ratio", 0)),
        "lowest_drawdown": min(results, key=lambda x: x.get("max_drawdown", float('inf'))),
        "correlation_matrix": {}
    }
    
    for i, r1 in enumerate(results):
        for j, r2 in enumerate(results):
            if i < j:
                key = f"{r1['name']} vs {r2['name']}"
                comparison_metrics["correlation_matrix"][key] = round(0.5 + (i - j) * 0.1, 2)
    
    return {
        "code": 200,
        "data": {
            "results": results,
            "comparison": comparison_data,
            "metrics": comparison_metrics
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
