from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    # 项目基本信息
    PROJECT_NAME: str = Field(default="Agents System", alias="PROJECT_NAME")
    PROJECT_VERSION: str = Field(default="1.0.0", alias="PROJECT_VERSION")
    DEBUG: bool = Field(default=False, alias="DEBUG")
    
    # 豆包大模型配置
    DOUBAO_API_KEY: Optional[str] = Field(default="15e0122b-bf1e-415f-873b-1cb6b39bb612", alias="DOUBAO_API_KEY")
    DOUBAO_MODEL_NAME: Optional[str] = Field(default="doubao-1-5-pro-32k-250115", alias="DOUBAO_MODEL_NAME")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", alias="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default="logs/agents_system.log", alias="LOG_FILE")

    DB_HOST: str = "localhost"
    DB_NAME: str = "zhongcan_RAG"
    DB_USER: str = "root"
    DB_PASSWORD: str = "12345678"
    EMBEDDING_MODEL: str = "doubao-embedding-large-text-250515"

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
        env_file_encoding = "utf-8"


settings = Settings()