from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'Document Writing Agent'
    llm_api_key: str = Field(default='', alias='DASHSCOPE_API_KEY')
    llm_base_url: str = Field(
        default='https://dashscope.aliyuncs.com/compatible-mode/v1',
        alias='QWEN_BASE_URL',
    )
    llm_model: str = Field(default='qwen-plus', alias='QWEN_MODEL')
    llm_timeout_seconds: int = Field(default=90, alias='QWEN_TIMEOUT_SECONDS')
    embedding_api_key: str = Field(default='', alias='DASHSCOPE_API_KEY')
    embedding_base_url: str = Field(
        default='https://dashscope.aliyuncs.com/compatible-mode/v1',
        alias='QWEN_EMBEDDING_BASE_URL',
    )
    embedding_model: str = Field(default='text-embedding-v3', alias='QWEN_EMBEDDING_MODEL')
    embedding_timeout_seconds: int = Field(default=60, alias='QWEN_EMBEDDING_TIMEOUT_SECONDS')
    firecrawl_api_key: str = Field(default='', alias='FIRECRAWL_API_KEY')
    firecrawl_timeout_seconds: int = Field(default=60, alias='FIRECRAWL_TIMEOUT_SECONDS')
    vector_store_dir: Path = Field(default=Path('storage/vector_store'), alias='VECTOR_STORE_DIR')
    uploads_dir: Path = Field(default=Path('storage/uploads'), alias='UPLOADS_DIR')
    knowledge_registry_path: Path = Field(default=Path('storage/knowledge_registry.json'), alias='KNOWLEDGE_REGISTRY_PATH')
    tavily_api_key: str = Field(default='', alias='TAVILY_API_KEY')
    allowed_origins: list[str] = Field(default=['http://localhost:5173'], alias='ALLOWED_ORIGINS')


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.vector_store_dir.mkdir(parents=True, exist_ok=True)
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.knowledge_registry_path.parent.mkdir(parents=True, exist_ok=True)
    if not settings.knowledge_registry_path.exists():
        settings.knowledge_registry_path.write_text('[]', encoding='utf-8')
    return settings
