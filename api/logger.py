"""
日志配置模块
"""

import sys
from pathlib import Path
from loguru import logger
from api.config import get_settings


settings = get_settings()


def setup_logger():
    """配置日志系统"""
    
    log_dir = Path(settings.logging.file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.remove()
    
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.logging.level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    logger.add(
        settings.logging.file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.logging.level,
        rotation=settings.logging.rotation,
        retention=settings.logging.retention,
        compression="zip",
        backtrace=True,
        diagnose=True,
        encoding="utf-8"
    )
    
    logger.info(f"日志系统初始化完成，级别: {settings.logging.level}")


def get_logger(name: str = None):
    """获取日志记录器"""
    if name:
        return logger.bind(name=name)
    return logger


class APILogger:
    """API请求日志记录器"""
    
    def __init__(self, name: str = "api"):
        self.logger = get_logger(name)
    
    def log_request(self, method: str, path: str, client_ip: str = None):
        """记录API请求"""
        log_msg = f"{method} {path}"
        if client_ip:
            log_msg += f" | IP: {client_ip}"
        self.logger.info(log_msg)
    
    def log_response(self, method: str, path: str, status_code: int, duration: float = None):
        """记录API响应"""
        log_msg = f"{method} {path} | Status: {status_code}"
        if duration:
            log_msg += f" | Duration: {duration:.3f}s"
        self.logger.info(log_msg)
    
    def log_error(self, method: str, path: str, error: str, status_code: int = 500):
        """记录API错误"""
        self.logger.error(f"{method} {path} | Status: {status_code} | Error: {error}")
    
    def log_validation_error(self, method: str, path: str, errors: list):
        """记录验证错误"""
        self.logger.warning(f"{method} {path} | Validation Errors: {errors}")
    
    def log_auth(self, username: str, action: str, success: bool = True):
        """记录认证事件"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"AUTH | User: {username} | Action: {action} | Status: {status}")
    
    def log_database(self, operation: str, collection: str, duration: float = None):
        """记录数据库操作"""
        log_msg = f"DB | {operation} | Collection: {collection}"
        if duration:
            log_msg += f" | Duration: {duration:.3f}s"
        self.logger.debug(log_msg)
    
    def log_cache(self, operation: str, key: str = None, hit: bool = None):
        """记录缓存操作"""
        log_msg = f"CACHE | {operation}"
        if key:
            log_msg += f" | Key: {key}"
        if hit is not None:
            log_msg += f" | Hit: {hit}"
        self.logger.debug(log_msg)


api_logger = APILogger("api")


def log_exception(logger_instance, exc: Exception, context: str = ""):
    """记录异常"""
    import traceback
    error_msg = f"Exception occurred"
    if context:
        error_msg += f" in {context}"
    error_msg += f": {str(exc)}"
    
    logger_instance.error(error_msg)
    logger_instance.debug(traceback.format_exc())


def log_performance(logger_instance, operation: str, duration: float, threshold: float = 1.0):
    """记录性能指标"""
    if duration > threshold:
        logger_instance.warning(f"PERFORMANCE | {operation} | Duration: {duration:.3f}s (Threshold: {threshold}s)")
    else:
        logger_instance.debug(f"PERFORMANCE | {operation} | Duration: {duration:.3f}s")


setup_logger()
