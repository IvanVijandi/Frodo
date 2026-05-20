import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Milvus Configuration
    MILVUS_URI: str = "http://localhost:19530"
    MILVUS_TOKEN: Optional[str] = None
    
    # Model Providers
    LLM_PROVIDER: str = "ollama"
    EMBEDDING_PROVIDER: str = "ollama"
    RERANKER_PROVIDER: str = "none"
    
    # Local URIs
    OLLAMA_URI: str = "http://localhost:11434"
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    VOYAGE_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Instancia global de configuracion
conf = Settings()
