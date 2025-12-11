"""Application configuration."""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Settings:
    """应用设置."""

    # 基本设置
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # API 设置
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_PREFIX: str = os.getenv("API_PREFIX", "/api")

    # 文件存储
    PAPERS_DIR: str = os.getenv("PAPERS_DIR", "papers")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "50")) * 1024 * 1024  # MB

    # Claude API
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Agent 设置
    WORKFLOW_CONFIG: Dict[str, Any] = {
        "papers_dir": PAPERS_DIR,
        "batch_size": int(os.getenv("BATCH_SIZE", "10")),
        "parallel_tasks": int(os.getenv("PARALLEL_TASKS", "3")),
    }

    PDF_CONFIG: Dict[str, Any] = {
        "papers_dir": PAPERS_DIR,
        "extract_images": os.getenv("EXTRACT_IMAGES", "true").lower() == "true",
        "extract_tables": os.getenv("EXTRACT_TABLES", "true").lower() == "true",
        "extract_formulas": os.getenv("EXTRACT_FORMULAS", "true").lower() == "true",
    }

    # 翻译设置
    TRANSLATION_CONFIG: Dict[str, Any] = {
        "target_language": os.getenv("TARGET_LANGUAGE", "zh"),
        "preserve_format": os.getenv("PRESERVE_FORMAT", "true").lower() == "true",
        "batch_size": int(os.getenv("TRANSLATION_BATCH_SIZE", "5000")),
    }

    # WebSocket 设置
    WS_HEARTBEAT_INTERVAL: int = int(os.getenv("WS_HEARTBEAT_INTERVAL", "30"))
    WS_CONNECTION_TIMEOUT: int = int(os.getenv("WS_CONNECTION_TIMEOUT", "600"))

    # 数据库设置（保留但暂不使用）
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

    # Redis 设置（保留但暂不使用）
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")

    # 安全设置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # CORS 设置
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

    # 日志设置
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    LOG_FILE: str = os.path.join(LOG_DIR, "app.log")
    LOG_MAX_SIZE: int = int(os.getenv("LOG_MAX_SIZE", "10")) * 1024 * 1024  # MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    @property
    def papers_path(self) -> Path:
        """获取论文目录路径."""
        return Path(self.PAPERS_DIR)

    @property
    def log_path(self) -> Path:
        """获取日志目录路径."""
        return Path(self.LOG_DIR)


# 创建全局设置实例
settings = Settings()
