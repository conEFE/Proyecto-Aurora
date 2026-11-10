# Revisión de seguridad OWASP Top 10 (2021) — Proyecto Aurora 2.3.0

Revisión del código del backend (FastAPI) y del frontend (React), hecha junto con la épica E6 (09-11-2026).
Los controles nombrados tienen pruebas automáticas en `backend/app/tests/` (principalmente
`test_account_security.py`, `test_auth.py` y `test_users_patients.py`).

**Alcance:** revisión de código, de configuración y de dependencias (`pip-audit` y `npm audit`). El escaneo
dinámico con OWASP ZAP necesita la aplicación desplegada, así que queda para la fase de infraestructura (S7).

## Hallazgos corregidos en la 2.3.0

| # | Categoría | Hallazgo | Corrección |
|---|---|---|---|
| 1 | A07 | Sin límite de intentos de login ni bloqueo de cuenta | Bloqueo de 15 min tras 5 fallos seguidos (423) y máximo de 10 intentos por IP por minuto (429 con `Retry-After`). Se audita como `LOGIN_FAIL` con su motivo |
| 2 | A07 | El usuario no podía cambiar su contraseña; la contraseña que asigna el ADMIN quedaba para siempre | `POST /auth/change-password` y cambio obligatorio en el primer ingreso o tras un restablecimiento |
| 3 | A07 | Cambiar o restablecer la contraseña no cerraba las sesiones abiertas | El token lleva una marca de la contraseña vigente; si no coincide, la API responde 401 |
| 4 | A07 | Política de contraseñas débil (solo 8 caracteres) | Mínimo 10 caracteres, con letras y números, distinta de la actual, sin el RUT y fuera de una lista de contraseñas comunes |
| 5 | A07 | Con un RUT inexistente la respuesta era más rápida (permitía saber qué RUT tienen cuenta) | Con un RUT inexistente igual se calcula un bcrypt, para que la respuesta tarde lo mismo |
| 6 | A04/A05 | `client_ip` confiaba en `X-Forwarded-For`: falsificando ese encabezado se evadía el límite por IP y se ensuciaba la auditoría | Solo se usa con `TRUST_PROXY_HEADERS=true` (detrás de un proxy propio), tomando la entrada que agrega el proxy |
| 7 | A02 | `SECRET_KEY` aceptaba claves cortas | La API no arranca con menos de 32 caracteres (256 bits para HS256) |
| 8 | A02/A06 | `python-jose` (y `ecdsa`, que llega con ella) tienen vulnerabilidades sin corrección | Se reemplazó por PyJWT, con la lista de algoritmos fija (`HS256`) y los claims `sub`, `exp` e `iat` obligatorios. Un token con `alg: none` se rechaza |
| 9 | A06 | Dependencias con vulnerabilidades conocidas: starlette 0.38.6, python-multipart 0.0.12, Pillow 11.0.0, jsPDF 3.0.4 (incluye DOMPurify y fflate) y black 26.10.0 | starlette 1.10.0 (con FastAPI 0.135.4), python-multipart 0.0.33, Pillow 13.0.0, jsPDF 4.2.1 con jspdf-autotable 5.0.9, black 26.10.1. `pip-audit` y `npm audit --omit=dev` quedan en 0 |
| 10 | A05 | La API no enviaba encabezados de seguridad | `X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy`, `Permissions-Policy`, HSTS, `Cache-Control: no-store` y una CSP restrictiva en las respuestas JSON |
| 11 | A05 | CORS permitía cualquier encabezado (`allow_headers=["*"]`) | Solo `Authorization` y `Content-Type` |
| 12 | A05 | `/docs` y `/openapi.json` siempre publicados | Se controlan con `ENABLE_API_DOCS` (desactivar en producción) |
| 13 | A09 | Los errores 5xx no quedaban registrados y el usuario no tenía cómo reportarlos | Tabla `error_log` sin datos sensibles (el mensaje se recorta y se le quitan SQL, parámetros, RUT, emails y números), `X-Request-ID` en cada respuesta, mensaje genérico con el código de la solicitud, vista para el ADMIN y conteo en el dashboard (K9) |
| 14 | A04 | El login aceptaba cuerpos de cualquier tamaño | Largo máximo del RUT (20) y de la contraseña (200) |

## Estado por categoría

| Categoría | Estado | Controles | Pendiente |
|---|---|---|---|
| **A01** Control de acceso roto | Cubierto | El rol se lee de la BD en cada request, nunca del token. Mínimo privilegio: el ADMIN no ve datos clínicos. Una prueba recorre **todas** las rutas y comprueba que respondan 401 sin token (salvo `/health` y `/auth/login`). Mientras el cambio de contraseña está pendiente, la API solo deja ver el perfil y cambiarla | Los casos los ve cualquier MEDICO o ADMINISTRATIVO (no hay asignación por paciente). Es una decisión de diseño de la especificación |
| **A02** Fallas criptográficas | Cubierto | bcrypt (12 rondas), imágenes cifradas con Fernet, JWT HS256 con clave de al menos 256 bits, HMAC-SHA256 en la firma del reporte, HSTS | TLS lo pone el despliegue (S7) |
| **A03** Inyección | Cubierto | ORM con parámetros. El único SQL literal es fijo (`nextval`). Pydantic valida toda entrada. React escapa la salida y no se usa `dangerouslySetInnerHTML` | — |
| **A04** Diseño inseguro | Cubierto | Bloqueo y límite de intentos, cambio obligatorio de contraseña, consentimiento obligatorio, IA simulada marcada siempre | — |
| **A05** Configuración insegura | Cubierto en la API | Encabezados de seguridad, CORS acotado, sin secretos por defecto, `/docs` configurable, errores sin detalles internos | CSP y encabezados del sitio estático del frontend: los pone el servidor web del despliegue (S7) |
| **A06** Componentes vulnerables | Producción en 0 | `pip-audit -r requirements.txt` y `npm audit --omit=dev`: sin hallazgos | Quedan avisos solo en herramientas de desarrollo (ESLint, Vite/esbuild 5.x): el arreglo exige subir Vite a una versión mayor. No llegan al build de producción. Revisión automática en CI (S7) |
| **A07** Fallas de identificación y autenticación | Cubierto | Ver hallazgos 1 a 5. Token de 30 minutos. Mensajes que no distinguen entre RUT inexistente y contraseña incorrecta | Una cuenta bloqueada responde distinto (423), lo que revela que el RUT existe. Se aceptó porque el bloqueo es temporal y el límite por IP frena la enumeración. Segundo factor (MFA) para la fase productiva |
| **A08** Fallas de integridad | Cubierto | SHA-256 del contenido del reporte y firma HMAC del médico, `package-lock.json` y versiones fijadas, bitácora append-only protegida por un trigger | Firmar las imágenes de contenedor en CI (S7) |
| **A09** Fallas de registro y monitoreo | Cubierto | `audit_log` append-only (LOGIN_OK/FAIL con motivo, PASSWORD_CHANGE/_FAIL, SIGN/_FAIL, CRUD), `error_log` y `request_metrics` | Alertas (CloudWatch) en el despliegue (S7) |
| **A10** SSRF | Cubierto | La única URL saliente (`INFERENCE_URL`) viene de la configuración, nunca del usuario | — |

## Riesgos aceptados y trabajo pendiente

- **Token en `localStorage`.** Un XSS podría leerlo. Lo mitigan: no se inserta HTML sin escapar, el token dura
  30 minutos y un cambio de contraseña lo revoca. La alternativa (cookie `HttpOnly` + protección CSRF) conviene
  evaluarla junto con el despliegue.
- **El límite por IP vive en memoria, por proceso.** Con varias réplicas, el límite se multiplica por el número
  de réplicas. El bloqueo por cuenta está en la BD y sigue funcionando igual. Con réplicas hay que moverlo a un
  almacén compartido (Redis) (S7).
- **Escaneo dinámico con OWASP ZAP** sobre el entorno de staging (S7).
- **Firma electrónica avanzada** (Ley 19.799) para la fase productiva: hoy la firma del reporte es simple
  (contraseña + HMAC + auditoría).

## Cómo repetir la revisión de dependencias

```bash
cd backend
pip install pip-audit
pip-audit -r requirements.txt -r requirements-dev.txt
cd ..
npm audit --omit=dev
```
