from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "DocuChat AI"
    DEBUG: bool = False

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gemini-2.0-flash-lite"
  

    # Chunking
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 100

    # Retrieval
    TOP_K: int = 5

    # Storage paths
    UPLOAD_DIR: str = "storage/uploads"
    FAISS_INDEX_DIR: str = "storage/faiss_index"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8501"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra="ignore"


settings = Settings()