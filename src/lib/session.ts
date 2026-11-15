import { apiClient } from '../services/api';

export const LOGOUT_REASON_KEY = 'aurora_logout_reason';

/** Cierra la sesión y deja el motivo para mostrarlo en la pantalla de ingreso. */
export function logoutForInactivity() {
  try {
    sessionStorage.setItem(LOGOUT_REASON_KEY, 'inactividad');
  } catch {
    /* sin almacenamiento: se cierra igual, sin el aviso */
  }
  apiClient.setToken(null);
  window.location.assign(`/ingresar`);
}

