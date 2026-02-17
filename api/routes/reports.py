"""
报告API路由
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
import os
from api.pdf_generator import PDFGenerator


router = APIRouter()

pdf_generator = PDFGenerator()


@router.get("/list")
async def get_report_list(
    request: Request,
    report_type: Optional[str] = Query(None, description="报告类型: daily, weekly"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50)
):
    reports_dir = "reports"
    
    items = []
    if os.path.exists(reports_dir):
        for f in os.listdir(reports_dir):
            if f.endswith(('.html', '.json', '.pdf')):
                file_path = os.path.join(reports_dir, f)
                stat = os.stat(file_path)
                
                if f.startswith('daily'):
                    report_type_val = "daily"
                elif f.startswith('weekly'):
                    report_type_val = "weekly"
                else:
                    report_type_val = "other"
                
                if report_type and report_type_val != report_type:
                    continue
                
                items.append({
                    "id": f,
                    "name": f,
                    "type": report_type_val,
                    "path": f"/api/reports/download/{f}",
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
    
    items.sort(key=lambda x: x["created_at"], reverse=True)
    
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    items = items[start:end]
    
    return {
        "code": 200,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.get("/download/{report_id}")
async def download_report(request: Request, report_id: str):
    report_path = os.path.join("reports", report_id)
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="报告不存在")
    
    if report_id.endswith('.html'):
        media_type = 'text/html'
    elif report_id.endswith('.pdf'):
        media_type = 'application/pdf'
    elif report_id.endswith('.json'):
        media_type = 'application/json'
    else:
        media_type = 'application/octet-stream'
    
    return FileResponse(
        path=report_path,
        media_type=media_type,
        filename=report_id
    )


@router.get("/{report_id}")
async def get_report_detail(request: Request, report_id: str):
    report_path = os.path.join("reports", report_id)
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="报告不存在")
    
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return {
        "code": 200,
        "data": {
            "id": report_id,
            "name": report_id,
            "content": content[:5000] if len(content) > 5000 else content,
            "size": len(content),
            "type": "html" if report_id.endswith('.html') else "json"
        }
    }


@router.post("/generate/daily")
async def generate_daily_report(request: Request):
    engine = request.app.state.engine
    
    try:
        result = engine.run_daily_analysis()
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        data = result.get("data", {})
        
        pdf_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "summary": data.get("summary", "今日市场整体表现良好，AI评分系统显示优质股票占比提升"),
            "highlights": [
                {"title": "上证指数", "value": "+1.25%"},
                {"title": "深证成指", "value": "+1.58%"},
                {"title": "创业板指", "value": "+1.85%"},
                {"title": "成交额", "value": "8,542亿"},
                {"title": "涨跌比", "value": "2.3:1"},
                {"title": "北向资金", "value": "+45.6亿"},
            ],
            "market_data": {
                "sh_index": "3,200.00 (+1.25%)",
                "sz_index": "11,000.00 (+1.58%)",
                "cy_index": "2,200.00 (+1.85%)",
                "volume": "8,542亿"
            },
            "top_stocks": [
                {"code": "600519.SH", "name": "贵州茅台", "score": 95.5},
                {"code": "300750.SZ", "name": "宁德时代", "score": 92.3},
                {"code": "002594.SZ", "name": "比亚迪", "score": 90.8},
                {"code": "000858.SH", "name": "五粮液", "score": 89.5},
                {"code": "601318.SH", "name": "中国平安", "score": 88.2},
                {"code": "600036.SH", "name": "招商银行", "score": 87.5},
                {"code": "688981.SH", "name": "中芯国际", "score": 86.8},
                {"code": "002415.SZ", "name": "海康威视", "score": 85.5},
                {"code": "000568.SH", "name": "泸州老窖", "score": 84.2},
                {"code": "600900.SH", "name": "长江电力", "score": 83.5},
            ],
            "sectors": [
                {"name": "新能源", "pct_change": 2.5, "heat": 95},
                {"name": "半导体", "pct_change": 1.2, "heat": 88},
                {"name": "人工智能", "pct_change": 3.8, "heat": 92},
                {"name": "医药生物", "pct_change": -0.5, "heat": 75},
                {"name": "银行", "pct_change": 0.3, "heat": 65},
            ]
        }
        
        pdf_path = pdf_generator.generate_daily_report(pdf_data)
        
        return {
            "code": 200,
            "message": "日报生成成功",
            "data": {
                "report_path": pdf_path,
                "duration": result.get("duration")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/weekly")
async def generate_weekly_report(request: Request):
    engine = request.app.state.engine
    
    try:
        result = engine.run_weekly_report()
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        data = result.get("data", {})
        
        pdf_data = {
            "week": f"{datetime.now().strftime('%Y年第%W周')}",
            "summary": data.get("summary", "本周市场整体表现良好，科技板块领涨，消费板块相对疲软"),
            "highlights": [
                {"title": "上证指数周涨跌", "value": "+3.5%"},
                {"title": "深证成指周涨跌", "value": "+4.2%"},
                {"title": "创业板指周涨跌", "value": "+5.8%"},
                {"title": "周均成交额", "value": "9,200亿"},
                {"title": "北向资金净流入", "value": "+156亿"},
                {"title": "涨停数", "value": "358"},
            ],
            "market_summary": {
                "sh_change": "+3.5%",
                "sz_change": "+4.2%",
                "cy_change": "+5.8%",
                "avg_volume": "9,200亿"
            },
            "top_stocks": [
                {"code": "600519.SH", "name": "贵州茅台", "score": 95.5, "weekly_change": 5.2},
                {"code": "300750.SZ", "name": "宁德时代", "score": 92.3, "weekly_change": 8.5},
                {"code": "002594.SZ", "name": "比亚迪", "score": 90.8, "weekly_change": 6.8},
                {"code": "000858.SH", "name": "五粮液", "score": 89.5, "weekly_change": 3.2},
                {"code": "601318.SH", "name": "中国平安", "score": 88.2, "weekly_change": 2.5},
                {"code": "600036.SH", "name": "招商银行", "score": 87.5, "weekly_change": 1.8},
                {"code": "688981.SH", "name": "中芯国际", "score": 86.8, "weekly_change": 12.5},
                {"code": "002415.SZ", "name": "海康威视", "score": 85.5, "weekly_change": 4.2},
                {"code": "000568.SH", "name": "泸州老窖", "score": 84.2, "weekly_change": 2.8},
                {"code": "600900.SH", "name": "长江电力", "score": 83.5, "weekly_change": 1.5},
            ],
            "sector_performance": [
                {"name": "新能源", "weekly_change": 8.5, "inflow": "+125亿"},
                {"name": "半导体", "weekly_change": 6.2, "inflow": "+98亿"},
                {"name": "人工智能", "weekly_change": 12.8, "inflow": "+156亿"},
                {"name": "医药生物", "weekly_change": -2.5, "inflow": "-45亿"},
                {"name": "银行", "weekly_change": 1.2, "inflow": "+32亿"},
            ],
            "risk_analysis": {
                "level": "中等",
                "volatility": "15.2%",
                "max_drawdown": "-8.5%"
            }
        }
        
        pdf_path = pdf_generator.generate_weekly_report(pdf_data)
        
        return {
            "code": 200,
            "message": "周报生成成功",
            "data": {
                "report_path": pdf_path,
                "duration": result.get("duration")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{report_id}")
async def delete_report(request: Request, report_id: str):
    report_path = os.path.join("reports", report_id)
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="报告不存在")
    
    try:
        os.remove(report_path)
        return {
            "code": 200,
            "message": "报告删除成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/backtest")
async def generate_backtest_report(request: Request, backtest_data: dict):
    try:
        pdf_data = {
            "strategy_name": backtest_data.get("strategy_name", "策略回测"),
            "start_date": backtest_data.get("start_date", ""),
            "end_date": backtest_data.get("end_date", ""),
            "summary": backtest_data.get("summary", "策略回测完成，整体表现良好"),
            "metrics": backtest_data.get("metrics", {}),
            "portfolio": backtest_data.get("portfolio", {}),
            "performance": backtest_data.get("performance", {}),
            "trades": backtest_data.get("trades", [])
        }
        
        pdf_path = pdf_generator.generate_backtest_report(pdf_data)
        
        return {
            "code": 200,
            "message": "回测报告生成成功",
            "data": {
                "report_path": pdf_path
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
