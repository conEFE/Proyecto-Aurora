"""Validación de RUT chileno (módulo 11)."""

import re

_RUT_RE = re.compile(r"^(\d{1,8})-([\dK])$")


def normalize_rut(value: str) -> str:
    """Quita puntos y espacios, y deja el dígito verificador en mayúscula: 12.345.678-k -> 12345678-K."""
    cleaned = value.replace(".", "").replace(" ", "").strip().upper()
    if "-" not in cleaned and len(cleaned) >= 2:
        cleaned = f"{cleaned[:-1]}-{cleaned[-1]}"
    return cleaned


def compute_dv(body: str) -> str:
    total, factor = 0, 2
    for digit in reversed(body):
        total += int(digit) * factor
        factor = 2 if factor == 7 else factor + 1
    remainder = 11 - (total % 11)
    if remainder == 11:
        return "0"
    if remainder == 10:
        return "K"
    return str(remainder)


def is_valid_rut(value: str) -> bool:
    match = _RUT_RE.match(normalize_rut(value))
    if not match:
        return False
    body, dv = match.groups()
    return compute_dv(body) == dv


def validate_rut(value: str) -> str:
    """Normaliza y valida; lanza ValueError con mensaje en español si no es válido."""
    rut = normalize_rut(value)
    if not is_valid_rut(rut):
        raise ValueError("RUT inválido: revise el dígito verificador")
    return rut
