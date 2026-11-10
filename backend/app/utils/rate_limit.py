"""Límite de solicitudes por clave en ventana deslizante, en memoria (por proceso).

Suficiente para una instancia; con varias instancias o workers el límite se multiplica, y el
bloqueo de cuenta (en la BD) sigue protegiendo cada usuario. Para producción con réplicas se
debe mover a un almacén compartido (p. ej. Redis), lo que queda para la fase de infraestructura.
"""

import threading
import time
from collections import deque


class SlidingWindowLimiter:
    def __init__(self, window_seconds: float = 60.0):
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = {}
        self._blocked_notified: set[str] = set()
        self._lock = threading.Lock()

    def hit(self, key: str, limit: int) -> tuple[bool, int, bool]:
        """Registra un intento. Devuelve (permitido, segundos_para_reintentar, primer_rechazo_de_la_ventana)."""
        now = time.monotonic()
        with self._lock:
            q = self._hits.setdefault(key, deque())
            while q and now - q[0] >= self.window:
                q.popleft()
            if not q:
                self._blocked_notified.discard(key)
            if len(q) >= limit:
                retry_after = max(1, int(self.window - (now - q[0])) + 1)
                first = key not in self._blocked_notified
                self._blocked_notified.add(key)
                return False, retry_after, first
            q.append(now)
            if len(self._hits) > 10_000:  # evita crecer sin límite ante muchas IP distintas
                self._purge(now)
            return True, 0, False

    def _purge(self, now: float) -> None:
        for k in [k for k, q in self._hits.items() if not q or now - q[-1] >= self.window]:
            del self._hits[k]
            self._blocked_notified.discard(k)

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()
            self._blocked_notified.clear()


login_limiter = SlidingWindowLimiter(60.0)
