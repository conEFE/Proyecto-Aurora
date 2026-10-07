/** Validación de RUT chileno (módulo 11), equivalente a backend/app/utils/rut.py. */

export function normalizeRut(value: string): string {
  let cleaned = value.replace(/[.\s]/g, '').trim().toUpperCase();
  if (!cleaned.includes('-') && cleaned.length >= 2) {
    cleaned = `${cleaned.slice(0, -1)}-${cleaned.slice(-1)}`;
  }
  return cleaned;
}

export function computeDv(body: string): string {
  let total = 0;
  let factor = 2;
  for (let i = body.length - 1; i >= 0; i--) {
    total += Number(body[i]) * factor;
    factor = factor === 7 ? 2 : factor + 1;
  }
  const remainder = 11 - (total % 11);
  if (remainder === 11) return '0';
  if (remainder === 10) return 'K';
  return String(remainder);
}

export function isValidRut(value: string): boolean {
  const match = /^(\d{1,8})-([\dK])$/.exec(normalizeRut(value));
  if (!match) return false;
  return computeDv(match[1]) === match[2];
}
