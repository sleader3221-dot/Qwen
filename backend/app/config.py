from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    app_name: str = "Enterprise AI Autopilot"
    app_version: str = "1.0.0"
    debug: bool = False

    # Qwen Cloud
    dashscope_api_key: str = ""
    qwen_model: str = "qwen3.6-plus"
    qwen_base_url: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    qwen_responses_url: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

    # Database
    database_url: str = "sqlite:///./autopilot.db"
    redis_url: str = "redis://localhost:6379/0"

    # Security
    secret_key: str = "super-secret-key-change-in-production"
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"

    # Email
    sendgrid_api_key: Optional[str] = None

    # Slack
    slack_bot_token: Optional[str] = None
    slack_signing_secret: Optional[str] = None

    # Alibaba Cloud
    alibaba_cloud_access_key_id: Optional[str] = None
    alibaba_cloud_access_key_secret: Optional[str] = None
    alibaba_cloud_region: str = "ap-southeast-1"
    alibaba_cloud_oss_bucket: Optional[str] = None

    # Feature Flags
    enable_thinking_mode: bool = True
    enable_web_search: bool = True
    enable_code_interpreter: bool = True
    enable_mcp_integration: bool = True
    enable_human_in_loop: bool = True
    confidence_threshold: float = 0.85
    max_retry_attempts: int = 3
    workflow_timeout_seconds: int = 300
    token_budget_daily: int = 1000000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def qwen_client_kwargs(self):
        return {
            "api_key": self.dashscope_api_key,
            "base_url": self.qwen_base_url,
        }


settings = Settings()
