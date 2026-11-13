from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    DB_DSN: str
    # Versión instalada (tag de las imágenes, p. ej. sha-<commit> o vX.Y.Z); la entrega docker compose
    AURORA_VERSION: str = "local"
    # Obligatorio y sin valor por defecto: la app no arranca si falta.
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Lista separada por comas
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    FILES_DIR: str = "./data/images"
    ENCRYPTION_KEY: str = ""
    # Clave anterior durante una rotación (scripts/rotate_secrets.py): solo se usa para descifrar
    ENCRYPTION_KEY_PREVIOUS: str = ""
    # Almacenamiento de imágenes: "local" (FILES_DIR) o "s3" (S3_BUCKET, cifrado además con SSE-KMS)
    STORAGE_BACKEND: str = "local"
    S3_BUCKET: str = ""
    S3_PREFIX: str = "images/"
    S3_KMS_KEY_ID: str = ""
    AWS_REGION: str = "us-east-2"
    MAX_UPLOAD_MB: int = 60
    BCRYPT_ROUNDS: int = 12

    # Proveedor de inferencia: "simulated" (por defecto) o "http" (servicio YOLO en INFERENCE_URL)
    INFERENCE_PROVIDER: str = "simulated"
    INFERENCE_URL: str = "http://localhost:8080"
    # Token compartido con el servicio de inferencia (Authorization: Bearer). Vacío = sin token (solo en local)
    INFERENCE_API_TOKEN: str = ""
    # En CPU (AWS) una imagen puede tardar varios segundos; con GPU, menos de uno
    INFERENCE_TIMEOUT_SECONDS: float = 60.0
    # Si el servicio no responde, usar la IA simulada (marcada) en vez de dejar la imagen sin resultado
    INFERENCE_FALLBACK_SIMULATED: bool = True

    # Guarda la duración de cada request en request_metrics (p95 del dashboard)
    REQUEST_METRICS_ENABLED: bool = True
    # Casos ALTA sin revisar por más de estas horas se marcan en el dashboard
    ALTA_PENDING_HOURS: int = 24

    # Seguridad de cuentas (E6)
    PASSWORD_MIN_LENGTH: int = 10
    # Intentos fallidos seguidos antes de bloquear la cuenta, y minutos de bloqueo
    LOGIN_MAX_FAILED_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15
    # Intentos de login por IP por minuto (límite en memoria, por proceso)
    LOGIN_RATE_LIMIT_PER_MINUTE: int = 10
    # Usar X-Forwarded-For para la IP del cliente: solo si la API está detrás de un proxy propio
    TRUST_PROXY_HEADERS: bool = False
    # Documentación interactiva (/docs, /redoc, /openapi.json); desactivar en producción
    ENABLE_API_DOCS: bool = True

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("SECRET_KEY no puede estar vacío")
        # HS256 necesita una clave de al menos 256 bits (OWASP A02)
        if len(v.encode("utf-8")) < 32:
            raise ValueError("SECRET_KEY debe tener al menos 32 caracteres")
        return v

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()
