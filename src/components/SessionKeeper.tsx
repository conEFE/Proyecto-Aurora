import { useEffect, useRef, useState } from 'react';
import { apiClient } from '../services/api';
import { logoutForInactivity } from '../lib/session';
import Dialog from './Dialog';
import { primaryButton, secondaryButton } from './ui';

/**
 * Sesión por inactividad: mientras la persona usa la plataforma (teclado, mouse, toque o desplazamiento) el token se
 * renueva; tras un rato sin actividad avisa y luego cierra la sesión. La actividad se comparte entre pestañas, así
 * que una pestaña en segundo plano no cierra la sesión de quien trabaja en otra.
 *
 * Los sondeos automáticos (cola, notificaciones) no cuentan como actividad.
 */

const ACTIVITY_KEY = 'aurora_last_activity';
const CHECK_MS = 10_000;
const WARN_MS = 60_000;
/** Margen para cerrar antes de que el token venza en el servidor. */
const SAFETY_MS = 90_000;
const DEFAULT_LIFETIME_MS = 30 * 60_000;

function tokenTimes(): { iat: number; exp: number } | null {
  try {
    const token = localStorage.getItem('auth_token');
    if (!token) return null;
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
    return { iat: payload.iat * 1000, exp: payload.exp * 1000 };
  } catch {
    return null;
  }
}

function readActivity(): number {
  try {
    return Number(localStorage.getItem(ACTIVITY_KEY)) || 0;
  } catch {
    return 0;
  }
}

function writeActivity(t: number) {
  try {
    localStorage.setItem(ACTIVITY_KEY, String(t));
  } catch {
    /* sin almacenamiento: la actividad se cuenta solo en esta pestaña */
  }
}

export default function SessionKeeper() {
  const lastActivity = useRef(Date.now());
  const lastRefresh = useRef(tokenTimes()?.iat ?? Date.now());
  const refreshing = useRef(false);
  const [secondsLeft, setSecondsLeft] = useState<number | null>(null);

  useEffect(() => {
    const now = Date.now();
    lastActivity.current = now;
    writeActivity(now);
    let lastWrite = 0;

    const onActivity = () => {
      const t = Date.now();
      lastActivity.current = t;
      // Escribe como máximo cada 5 s (para avisar a las otras pestañas sin sobrecargar)
      if (t - lastWrite > 5_000) {
        lastWrite = t;
        writeActivity(t);
      }
    };
    const events: Array<keyof WindowEventMap> = ['pointerdown', 'keydown', 'wheel', 'touchstart', 'mousemove', 'scroll'];
    events.forEach((e) => window.addEventListener(e, onActivity, { passive: true }));

    const tick = async () => {
      const t = Date.now();
      const latest = Math.max(lastActivity.current, readActivity());
      const times = tokenTimes();
      if (!times) return;
      const lifetime = times.exp - times.iat || DEFAULT_LIFETIME_MS;
      const idleLimit = lifetime - SAFETY_MS;
      const idle = t - latest;

      if (idle >= idleLimit || t >= times.exp) {
        logoutForInactivity();
        return;
      }
      if (idle >= idleLimit - WARN_MS) {
        setSecondsLeft(Math.max(1, Math.round((idleLimit - idle) / 1000)));
        return;
      }
      setSecondsLeft(null);
      // Hubo actividad desde la última renovación: se renueva (como mucho una vez por minuto)
      if (latest > lastRefresh.current && t - lastRefresh.current > 60_000 && !refreshing.current) {
        refreshing.current = true;
        const ok = await apiClient.refreshSession();
        refreshing.current = false;
        if (ok) lastRefresh.current = Date.now();
      }
    };

    const id = window.setInterval(tick, CHECK_MS);
    // Al volver a la pestaña se revisa de inmediato (los intervalos se frenan en segundo plano)
    const onVisible = () => document.visibilityState === 'visible' && tick();
    document.addEventListener('visibilitychange', onVisible);
    return () => {
      window.clearInterval(id);
      document.removeEventListener('visibilitychange', onVisible);
      events.forEach((e) => window.removeEventListener(e, onActivity));
    };
  }, []);

  // Cuenta regresiva del aviso, segundo a segundo
  useEffect(() => {
    if (secondsLeft === null) return;
    if (secondsLeft <= 0) {
      logoutForInactivity();
      return;
    }
    const id = window.setTimeout(() => setSecondsLeft((s) => (s === null ? null : s - 1)), 1000);
    return () => window.clearTimeout(id);
  }, [secondsLeft]);

  const keepWorking = async () => {
    const t = Date.now();
    lastActivity.current = t;
    writeActivity(t);
    setSecondsLeft(null);
    if (await apiClient.refreshSession()) lastRefresh.current = Date.now();
  };

  return (
    <Dialog
      open={secondsLeft !== null}
      onOpenChange={(open) => !open && keepWorking()}
      title="¿Sigue ahí?"
      description="Por seguridad, la sesión se cierra tras un rato sin actividad."
      footer={
        <>
          <button className={secondaryButton} onClick={logoutForInactivity}>Cerrar sesión</button>
          <button className={primaryButton} onClick={keepWorking} autoFocus>Seguir trabajando</button>
        </>
      }
    >
      <p className="text-sm" role="timer" aria-live="polite">
        Su sesión se cerrará en <strong className="tabular-nums">{secondsLeft ?? 0} s</strong>. Lo que no haya guardado
        se perderá.
      </p>
    </Dialog>
  );
}
