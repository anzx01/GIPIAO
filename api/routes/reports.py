"""
报告API路由
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
import os


router = APIRouter()


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
        
        return {
            "code": 200,
            "message": "日报生成成功",
            "data": {
                "report_path": result.get("data", {}).get("report_path"),
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
        
        return {
            "code": 200,
            "message": "周报生成成功",
            "data": {
                "report_path": result.get("report_path"),
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
