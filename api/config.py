"""
配置管理模块
统一管理环境变量和配置文件
"""

from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class DatabaseConfig(BaseModel):
    """数据库配置"""
    host: str = Field(default="localhost", description="MongoDB主机")
    port: int = Field(default=27017, description="MongoDB端口")
    user: Optional[str] = Field(default=None, description="MongoDB用户名")
    password: Optional[str] = Field(default=None, description="MongoDB密码")
    db_name: str = Field(default="aiqrh", description="数据库名称")
    
    @property
    def connection_string(self) -> str:
        """获取数据库连接字符串"""
        if self.user and self.password:
            return f"mongodb://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
        return f"mongodb://{self.host}:{self.port}/{self.db_name}"


class JWTConfig(BaseModel):
    """JWT配置"""
    secret_key: str = Field(default="your-secret-key-change-in-production", description="JWT密钥")
    algorithm: str = Field(default="HS256", description="JWT算法")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间（分钟）")


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = Field(default="INFO", description="日志级别")
    file: str = Field(default="logs/app.log", description="日志文件路径")
    rotation: str = Field(default="100 MB", description="日志轮转大小")
    retention: str = Field(default="30 days", description="日志保留时间")


class CacheConfig(BaseModel):
    """缓存配置"""
    enabled: bool = Field(default=True, description="是否启用缓存")
    ttl: int = Field(default=3600, description="默认缓存时间（秒）")
    max_size: int = Field(default=1000, description="最大缓存条目数")


class APIConfig(BaseModel):
    """API配置"""
    host: str = Field(default="0.0.0.0", description="API主机")
    port: int = Field(default=8001, description="API端口")
    reload: bool = Field(default=True, description="是否启用热重载")
    cors_origins: list = Field(default=["*"], description="CORS允许的来源")
    
    @property
    def base_url(self) -> str:
        """获取API基础URL"""
        return f"http://{self.host}:{self.port}"


class DataConfig(BaseModel):
    """数据配置"""
    dir: str = Field(default="data", description="数据目录")
    cache_enabled: bool = Field(default=True, description="是否启用数据缓存")
    cache_ttl: int = Field(default=3600, description="数据缓存时间（秒）")
    primary_source: str = Field(default="akshare", description="主要数据源")


class Settings(BaseSettings):
    """应用设置"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    jwt: JWTConfig = Field(default_factory=JWTConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    data: DataConfig = Field(default_factory=DataConfig)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.database = DatabaseConfig(
            host=os.getenv("MONGO_HOST", "localhost"),
            port=int(os.getenv("MONGO_PORT", "27017")),
            user=os.getenv("MONGO_USER"),
            password=os.getenv("MONGO_PASSWORD"),
            db_name=os.getenv("MONGO_DB", "aiqrh")
        )
        
        self.jwt = JWTConfig(
            secret_key=os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production"),
            algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        )
        
        self.logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            file=os.getenv("LOG_FILE", "logs/app.log"),
            rotation=os.getenv("LOG_ROTATION", "100 MB"),
            retention=os.getenv("LOG_RETENTION", "30 days")
        )
        
        self.cache = CacheConfig(
            enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
            ttl=int(os.getenv("CACHE_TTL", "3600")),
            max_size=int(os.getenv("CACHE_MAX_SIZE", "1000"))
        )
        
        self.api = APIConfig(
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "8001")),
            reload=os.getenv("API_RELOAD", "true").lower() == "true",
            cors_origins=os.getenv("CORS_ORIGINS", "*").split(",")
        )
        
        self.data = DataConfig(
            dir=os.getenv("DATA_DIR", "data"),
            cache_enabled=os.getenv("DATA_CACHE_ENABLED", "true").lower() == "true",
            cache_ttl=int(os.getenv("DATA_CACHE_TTL", "3600")),
            primary_source=os.getenv("DATA_SOURCE", "akshare")
        )


settings = Settings()


def get_settings() -> Settings:
    """获取应用设置"""
    return settings


def reload_settings() -> Settings:
    """重新加载设置"""
    global settings
    settings = Settings()
    return settings
