"""Política mínima de contraseñas (OWASP A07). Los mensajes de error van en español."""

import re

from app.config import settings
from app.services.errors import ValidationError

# Contraseñas muy comunes que se rechazan aunque cumplan el largo
_COMMON = {
    "1234567890",
    "12345678910",
    "0123456789",
    "contraseña123",
    "contrasena123",
    "password123",
    "password1234",
    "qwerty12345",
    "aurora12345",
    "admin12345",
    "abc1234567",
}


def policy_errors(password: str, rut: str | None = None, current_hash: str | None = None) -> list[str]:
    """Devuelve la lista de reglas que no se cumplen (vacía si la contraseña es aceptable)."""
    from app.auth.security import verify_password

    errors: list[str] = []
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        errors.append(f"debe tener al menos {settings.PASSWORD_MIN_LENGTH} caracteres")
    if len(password.encode("utf-8")) > 72:
        errors.append("no puede superar los 72 bytes")
    if not re.search(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]", password) or not re.search(r"\d", password):
        errors.append("debe combinar letras y números")
    if password.strip().lower() in _COMMON:
        errors.append("es demasiado común")
    if rut:
        body = rut.split("-")[0]
        if len(body) >= 6 and body in re.sub(r"\D", "", password):
            errors.append("no puede contener su RUT")
    if current_hash and verify_password(password, current_hash):
        errors.append("debe ser distinta de la contraseña actual")
    return errors


def ensure_valid_password(password: str, rut: str | None = None, current_hash: str | None = None) -> None:
    errors = policy_errors(password, rut, current_hash)
    if errors:
        raise ValidationError("La contraseña " + "; ".join(errors) + ".")
