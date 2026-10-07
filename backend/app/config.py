from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    DB_DSN: str
    # Obligatorio y sin valor por defecto: la app no arranca si falta.
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Lista separada por comas
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    FILES_DIR: str = "./data/images"
    ENCRYPTION_KEY: str = ""
    MAX_UPLOAD_MB: int = 60
    BCRYPT_ROUNDS: int = 12

    # Proveedor de inferencia: "simulated" (por defecto) o "http" (servicio YOLO en INFERENCE_URL)
    INFERENCE_PROVIDER: str = "simulated"
    INFERENCE_URL: str = "http://localhost:8080"

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("SECRET_KEY no puede estar vacío")
        return v

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()
