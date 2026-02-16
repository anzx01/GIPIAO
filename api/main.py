"""
AI Quant Research Hub - FastAPI Application
量化研究平台后端API服务
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger

from api.routes import stocks, portfolio, backtest, reports, market
from api.routes.auth import router as auth_router
from core.engine import QuantEngine


engine = None


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
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
