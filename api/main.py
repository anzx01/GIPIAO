"""
AI Quant Research Hub - FastAPI Application
量化研究平台后端API服务
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import Request, status
from fastapi.responses import JSONResponse
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from api.routes import stocks, portfolio, backtest, reports, market
from api.routes.auth import router as auth_router
from core.engine import QuantEngine
from api.config import get_settings
from api.logger import api_logger, log_exception


settings = get_settings()
engine = None


class APIError(Exception):
    """自定义API错误"""
    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code
        super().__init__(self.message)


async def api_error_handler(request: Request, exc: APIError):
    """API错误处理器"""
    api_logger.log_error(request.method, str(request.url.path), exc.message, exc.code)
    return JSONResponse(
        status_code=exc.code,
        content={"detail": exc.message, "code": exc.code}
    )


async def validation_error_handler(request: Request, exc: Exception):
    """验证错误处理器"""
    api_logger.log_validation_error(request.method, str(request.url.path), [str(exc)])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc), "code": 422}
    )


async def not_found_error_handler(request: Request, exc: Exception):
    """404错误处理器"""
    api_logger.log_error(request.method, str(request.url.path), "Resource not found", 404)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Resource not found", "code": 404}
    )


async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    log_exception(api_logger.logger, exc, f"{request.method} {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "code": 500}
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    logger.info("正在启动AI Quant Engine...")
    engine = QuantEngine("config.yaml")
    logger.info("引擎启动完成")
    app.state.engine = engine
    yield
    logger.info("正在关闭服务...")


app = FastAPI(
    title="AI Quant Research Hub API",
    description="AI量化研究平台后端API服务",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(status.HTTP_422_UNPROCESSABLE_ENTITY, validation_error_handler)
app.add_exception_handler(status.HTTP_404_NOT_FOUND, not_found_error_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(auth_router)
app.include_router(stocks.router, prefix="/api/stocks", tags=["股票"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["组合"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["回测"])
app.include_router(reports.router, prefix="/api/reports", tags=["报告"])
app.include_router(market.router, prefix="/api/market", tags=["市场"])


@app.get("/")
async def root():
    return {
        "name": "AI Quant Research Hub API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "认证": {
                "POST /api/auth/login": "用户登录",
                "POST /api/auth/register": "用户注册",
                "GET /api/auth/me": "获取当前用户",
            },
            "股票": {
                "GET /api/stocks/list": "股票列表",
                "GET /api/stocks/scores": "AI评分",
                "GET /api/stocks/{code}": "股票详情",
                "GET /api/stocks/{code}/price": "价格数据",
                "GET /api/stocks/{code}/indicators": "技术指标",
            },
            "市场": {
                "GET /api/market/summary": "市场概览",
                "GET /api/market/indices": "指数行情",
            },
            "组合": {
                "GET /api/portfolio/list": "组合列表",
                "POST /api/portfolio": "创建组合",
            },
            "回测": {
                "POST /api/backtest/run": "运行回测",
                "GET /api/backtest/history": "回测历史",
            },
            "报告": {
                "GET /api/reports/list": "报告列表",
                "POST /api/reports/generate/daily": "生成日报",
                "POST /api/reports/generate/weekly": "生成周报",
            }
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/cache/stats")
async def get_cache_stats():
    """获取缓存统计信息"""
    from api.cache import get_cache_stats
    return get_cache_stats()


@app.post("/cache/clear")
async def clear_cache_endpoint(pattern: str = ""):
    """清除缓存"""
    from api.cache import clear_cache
    clear_cache(pattern)
    return {"message": "Cache cleared", "pattern": pattern}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
