# Escaneo OWASP ZAP baseline — 24-11-2026

**Resultado: aprobado (PS-04).** 0 alertas de riesgo alto; 1 media y 3 bajas, todas sobre encabezados HTTP del
sitio estático. Dos bajas se corrigieron el mismo día; la media y una baja quedan como riesgo aceptado.

## Ejecución
- Workflow «ZAP baseline» (`.github/workflows/zap.yml`) de GitHub Actions, corrida 45401875332, sobre `main`
  (`e8d0144`, versión 2.10.2). ZAP 2.17.0, `zap-baseline.py` (araña 1 minuto + análisis pasivo, sin ataques).
- Objetivo: el stack completo (Caddy, sitio y API) levantado con Docker Compose **dentro del CI**, con secretos
  desechables y sin datos; no se escaneó `demo.auroracare.cl`. La configuración de Caddy y las imágenes son las mismas
  que en producción.
- Alcance alcanzado: la araña solo recorrió el sitio estático (página, `assets`, `favicon`, `robots.txt`,
  `sitemap.xml`): la aplicación es una SPA y la API exige token, así que la API autenticada **no** quedó cubierta.
- Archivos: `zap-sitio.html` (informe legible) y `zap-sitio.json`.

## Hallazgos
| Riesgo | Id | Alerta | Decisión |
|---|---|---|---|
| Medio | 10055 | CSP: `style-src 'unsafe-inline'` | Riesgo aceptado: la landing inyecta un `<style>` propio; `script-src 'self'` sigue bloqueando scripts en línea. |
| Bajo | 90004 | Falta `Cross-Origin-Opener-Policy` | Corregido (`same-origin`, `a2f4da4`). |
| Bajo | 90004 | Falta `Cross-Origin-Resource-Policy` | Corregido (`same-origin`, `a2f4da4`). |
| Bajo | 90004 | Falta `Cross-Origin-Embedder-Policy` | Riesgo aceptado: solo se requiere para el aislamiento entre orígenes (`SharedArrayBuffer`), que no se usa. |
| Informativo | 10109, 10049 | Aplicación web moderna; contenido almacenable en caché | Sin acción (los `assets` tienen nombre con hash y caché larga a propósito). |

Corrección desplegada en `demo.auroracare.cl` el 24-11-2026 (imagen `sha-a2f4da4…`); verificado con `curl -I` (los dos
encabezados presentes) y con un navegador (landing y login sin errores de consola ni imágenes rotas).

## Pendiente
Un escaneo autenticado de la API (contexto de ZAP con token) y un escaneo activo en un entorno de pruebas.
