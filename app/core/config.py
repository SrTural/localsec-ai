from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "LocalSec-AI"
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    COLLECTION_NAME: str = "security_logs"

    class Config:
        env_file = ".env"


settings = Settings()
