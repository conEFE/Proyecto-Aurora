export const PASSWORD_MIN_LENGTH = 10;

/** Reglas de la política mostradas en pantalla (el backend es quien valida y decide). */
export function passwordHints(password: string): { label: string; ok: boolean }[] {
  return [
    { label: `Al menos ${PASSWORD_MIN_LENGTH} caracteres`, ok: password.length >= PASSWORD_MIN_LENGTH },
    { label: 'Letras y números', ok: /[A-Za-zÁÉÍÓÚÑáéíóúñ]/.test(password) && /\d/.test(password) },
  ];
}
