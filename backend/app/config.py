from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union

class Settings(BaseSettings):
    DB_DSN: str
    FILES_DIR: str = "./data/images"
    INFERENCE_URL: str = "http://localhost:8080"
    ALLOWED_ORIGINS: Union[str, List[str]] = "http://localhost:5173,http://localhost:3000"
    SECRET_KEY: str = "demo-secret-key"
    ENCRYPTION_KEY: str = ""  # Se genera automáticamente si está vacío
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            # Si es string, separar por comas y limpiar espacios
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

settings = Settings()