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
from api.validators import validate_report_id


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
    report_path = validate_report_id(report_id)

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
    report_path = validate_report_id(report_id)

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
        pdf_payload = data.get("report_payload")
        
        if not pdf_payload:
            raise HTTPException(status_code=503, detail="日报真实数据载荷不可用")
        
        pdf_path = pdf_generator.generate_daily_report(pdf_payload)
        
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
        
        pdf_data = data.get("report_payload") or {
            "week": f"{datetime.now().strftime('%Y年第%W周')}",
            "summary": data.get("summary", ""),
            "highlights": data.get("highlights", []),
            "market_summary": data.get("market_summary", {}),
            "top_stocks": data.get("stock_scores", [])[:10],
            "sector_performance": data.get("sector_performance", []),
            "risk_analysis": data.get("risk_metrics", {}),
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
    report_path = validate_report_id(report_id)

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
            "strategy_name": backtest_data.get("strategy_name", ""),
            "start_date": backtest_data.get("start_date", ""),
            "end_date": backtest_data.get("end_date", ""),
            "summary": backtest_data.get("summary", ""),
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
