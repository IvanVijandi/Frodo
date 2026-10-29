
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Milvus Configuration
    MILVUS_URI: str = "http://localhost:19530"
    MILVUS_TOKEN: Optional[str] = None
    VECTOR_DIM: int = 768
    
    # Model Providers
    LLM_PROVIDER: str = "ollama"
    EMBEDDING_PROVIDER: str = "ollama"
    RERANKER_PROVIDER: str = "local"
    
    # Model Names
    LLM_MODEL: str = "qwen3.5:4b"
    EMBEDDING_MODEL: str = "embeddinggemma"
    EVALUATOR_MODEL: Optional[str] = None
    RERANKER_MODEL: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
    RERANKER_TOP_K: int = 3
    RERANKER_DEVICE: Optional[str] = None
    HF_HOME: Optional[str] = None
    
    # Local URIs
    OLLAMA_URI: str = "http://localhost:11434"
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    VOYAGE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # PostgreSQL Configuration
    POSTGRES_USER: str = "maria_user"
    POSTGRES_PASSWORD: str = "maria_pass"
    POSTGRES_DB: str = "maria_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Instancia global de configuracion
conf = Settings()
