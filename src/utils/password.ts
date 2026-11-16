export const PASSWORD_MIN_LENGTH = 10;

/** Reglas de la política mostradas en pantalla (el backend es quien valida y decide). */
export function passwordHints(password: string): { label: string; ok: boolean }[] {
  return [
    { label: `Al menos ${PASSWORD_MIN_LENGTH} caracteres`, ok: password.length >= PASSWORD_MIN_LENGTH },
    { label: 'Letras y números', ok: /[A-Za-zÁÉÍÓÚÑáéíóúñ]/.test(password) && /\d/.test(password) },
  ];
}

// Sin caracteres que se confunden al dictarla o copiarla a mano (0/O, 1/l/I)
const LETTERS = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ';
const DIGITS = '23456789';

function randomIndex(max: number): number {
  const buf = new Uint32Array(1);
  // Descarta valores del borde para que todos los caracteres salgan con la misma probabilidad
  const limit = Math.floor(0x1_0000_0000 / max) * max;
  do crypto.getRandomValues(buf);
  while (buf[0] >= limit);
  return buf[0] % max;
}

/**
 * Contraseña temporal al azar, en tres grupos de cuatro (p. ej. «hT7k-Wq3m-Rz8p»). Lleva 3 números sueltos (nunca 6
 * seguidos, así no puede contener un RUT) y cumple la política.
 */
export function generateTempPassword(): string {
  const chars = Array.from({ length: 12 }, () => LETTERS[randomIndex(LETTERS.length)]);
  const slots = Array.from({ length: 12 }, (_, i) => i);
  for (let n = 0; n < 3; n++) {
    const [slot] = slots.splice(randomIndex(slots.length), 1);
    chars[slot] = DIGITS[randomIndex(DIGITS.length)];
  }
  return [chars.slice(0, 4), chars.slice(4, 8), chars.slice(8)].map((g) => g.join('')).join('-');
}
