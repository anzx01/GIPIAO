import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import loguru


class AppLogger:
    """应用日志管理器"""
    
    _instance = None
    
    def __new__(cls, config: dict = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config: dict = None):
        if self._initialized:
            return
        
        self.config = config or {}
        self._initialized = True
        
        self._setup_logger()
    
    def _setup_logger(self):
        """设置日志"""
        
        log_dir = Path(self.config.get('log_dir', 'logs'))
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"aiqrh_{datetime.now().strftime('%Y%m%d')}.log"
        
        loguru.logger.remove()
        
        loguru.logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            level=self.config.get('level', 'INFO'),
            colorize=True
        )
        
        loguru.logger.add(
            str(log_file),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
            level=self.config.get('level', 'INFO'),
            rotation=self.config.get('rotation', '100 MB'),
            retention=self.config.get('retention', '30 days'),
            compression='zip'
        )
        
        loguru.logger.info("日志系统初始化完成")
    
    def get_logger(self):
        """获取日志实例"""
        return loguru.logger
    
    def log_execution(self, func_name: str, status: str, 
                     duration: float = None, error: str = None):
        """记录执行日志"""
        
        msg = f"执行 {func_name} - 状态: {status}"
        
        if duration is not None:
            msg += f" - 耗时: {duration:.2f}秒"
        
        if error:
            loguru.logger.error(f"{msg} - 错误: {error}")
        else:
            loguru.logger.info(msg)
    
    def log_performance(self, metric: str, value: float, unit: str = ''):
        """记录性能指标"""
        loguru.logger.info(f"性能指标 - {metric}: {value} {unit}")
    
    def log_error(self, error: Exception, context: str = ''):
        """记录错误"""
        if context:
            loguru.logger.error(f"{context} - 错误: {str(error)}")
        else:
            loguru.logger.error(f"错误: {str(error)}")
        
        import traceback
        loguru.logger.debug(traceback.format_exc())


def setup_logging(config: dict = None) -> AppLogger:
    """设置日志"""
    logger = AppLogger(config)
    return logger


def get_logger() -> loguru.Logger:
    """获取日志实例"""
    return loguru.logger
