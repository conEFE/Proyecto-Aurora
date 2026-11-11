# Estado del despliegue en AWS y plan para continuar

Actualizado: 11-11-2026 (noche). Desplegado: **2.9.2 + `9a3a942`** (Mi perfil, historia del paciente y textos de la IA),
imágenes `sha-9a3a942…` de `main`. **Modelo real conectado** (PC de Juan por Tailscale).
Sin migraciones nuevas desde la 2.6.0. Lo que trajo cada versión está en `docs/CHANGELOG_SPRINTS.md`:

- **2.8.0:** eliminar pacientes sin casos (con casos, bloqueo por la Ley 20.584), informe de gestión en PDF y
  `scripts/seed_demo.py`.
- **2.9.0:** nombre «Aurora Care», landing pública con acceso al login, sección Pacientes y un caso por examen con
  varias imágenes («Nuevo caso» con imágenes y «Agregar imágenes» en el caso; se quitó «Cargar imágenes»).
- **2.9.1:** reportes PDF con el diseño de la interfaz (tipografía Atkinson incrustada, paleta y timbres de nivel).
- **2.9.2:** informe de gestión con relato (resumen, hallazgos, gráficos, lectura por sección y recomendaciones).
- **`702bf84`:** el `Dockerfile` del sitio compila el frontend sin emulación (`--platform=$BUILDPLATFORM`): con QEMU,
  `npm ci` para arm64 tardaba más de 40 minutos y la publicación quedaba colgada.
- **`d082d4b` + `9a3a942` (sin número de versión aún):** textos de la IA alineados con el modelo (probabilidad de
  malignidad de la CNN, confianza de detección de YOLO), **Mi perfil** e **historia del paciente**. Respaldo previo:
  `backups/aurora-20261111T193250Z.sql.gz`.

**Datos de demostración en producción (11-11-2026):** `python -m scripts.seed_demo` cargó 120 pacientes ficticios (RUT
desde 40.000.000) y 134 casos en 10 semanas, a nombre del médico de prueba (`11111111-1`). Respaldo previo:
`backups/aurora-20261111T145234Z.sql.gz` (restaurarlo para quitarlos; la auditoría no permite borrar). Para la demo,
entrar como el médico de prueba: es quien ve el informe completo, incluido el desempeño del modelo.
**Hecho (11-11-2026, con `9a3a942`):** `python -m scripts.seed_demo --fix-history` dejó el registro y el
consentimiento de los 120 pacientes antes de sus casos, y los ajustes de nivel antes de la revisión. Solo toca RUT
desde 40.000.000 y se puede repetir sin efecto.

## 1. Qué está funcionando

| Pieza | Detalle |
|---|---|
| Sitio | **https://demo.auroracare.cl** (desde el 11-11-2026) y, en paralelo, https://13-184-207-158.sslip.io. HTTPS de Let's Encrypt, renovación automática por Caddy |
| Proyecto de AWS | Nueva experiencia de AWS, **plan gratuito**, región fija **us-east-2** (Ohio). Vence el **10-05-2027** |
| Créditos | **USD 180** al 10-11-2026 (100 iniciales + 80 de actividades). Pendiente: actividad de RDS (+20) |
| Servidor | EC2 `aurora-prod` (`i-0f7427c0dac2fd6b0`), `t4g.micro` arm64, Amazon Linux 2023, disco 10 GB gp3 cifrado, IMDSv2, créditos de CPU «estándar», 2 GB de swap |
| IP fija | Elastic IP `13.184.207.158` (etiqueta `Name=aurora-prod`) |
| Firewall | Grupo `aurora-web`: TCP 80, TCP 443 y UDP 443 desde Internet. **Sin puerto 22** |
| Acceso al servidor | **Session Manager** (EC2 → Conectar → Administrador de sesiones), luego `sudo su - ec2-user` |
| Rol | `AuroraEC2Role` = política `AuroraEC2` (S3 `images/*` y `backups/*`, logs `/aurora/*`) + `AmazonSSMManagedInstanceCore` |
| Contenedores | `/opt/aurora`: `db` (PostgreSQL 16), `backend` (API), `web` (Caddy + sitio). Configuración en `deploy/.env` (permisos 600, generado en el servidor; **sus secretos nunca salieron del servidor**) |
| Imágenes | Bucket privado `aurora-imagenes-7k3p9x`: cifrado Fernet (aplicación) + SSE-KMS `aws/s3`, versionado, acceso público bloqueado |
| Ciclo de vida del bucket | Versiones antiguas: 7 días. Respaldos (`backups/`): 35 días. Cargas incompletas: 7 días |
| Respaldo | `deploy/backup_db.sh` diario a las **03:15 hora de Chile** (crontab de `ec2-user`), verificado (13,5 KB) |
| Logs | CloudWatch `/aurora/prod` (backend, db, web), retención 30 días |
| DNS | Route 53, zona `auroracare.cl` (`Z0628464DNWEOT5ICYNC`), registro `demo` → Elastic IP. Delegado en NIC Chile (inscrito el 11-11-2026, vence el 11-11-2027) |
| Tailscale | Instalado en el servidor (11-11-2026): `aurora-ec2`, IP `100.83.18.31`, `--accept-dns=false`, servicio `tailscaled` habilitado al arrancar. Falta Juan (`aurora-modelo`) |
| Presupuesto | `aurora-mensual`: USD 15 al mes, alertas al 85 %, 100 % y pronóstico |
| Modelo de IA | `INFERENCE_PROVIDER=http`, `INFERENCE_URL=http://100.114.99.23:8080` (PC de Juan, `aurora-modelo`, GPU `cuda:0`). Si no responde, se usa la IA simulada con su badge (`INFERENCE_FALLBACK_SIMULATED=true`) |
| Usuarios | ADMIN (Felipe, con email provisorio `admin@aurora-demo.cl`) y médico de prueba `11111111-1` (ficticio) |

**Costo estimado:** ≈ USD 11 al mes, descontados de los créditos (alcanza para todo el plan gratuito).

## 2. Plan para continuar

### Próxima presentación (CRUD + informe de gestión)
- **Guion sugerido:** landing → Ingresar → Pacientes: crear, editar y eliminar un paciente sin casos (con casos aparece
  el aviso de la Ley 20.584) → «Nuevo caso» desde el paciente con varias imágenes (el lado se deduce del nombre:
  `R_CC`, `LMLO`…) → Administración: crear un usuario (contraseña temporal; cambio obligatorio en el primer ingreso)
  y desactivarlo → Dashboard → «Exportar informe PDF».
- **Pendiente de Felipe:** nombres y roles del equipo para tarjetas en «Quiénes somos» de la landing (hoy el texto es
  genérico, sin nombres inventados).
- **Opcional:** enlace de invitación para cuentas nuevas (no existe; hoy es contraseña temporal + cambio obligatorio).

### Prioridad alta
1. **Actividad de RDS (+USD 20):** iniciarla desde *Earn AWS credits*. Usar **RDS PostgreSQL** (no Aurora),
   capa gratuita, `db.t4g.micro`, una zona, 20 GB sin autoescalado y sin acceso público. Cuando aparezca completada,
   **borrarla** sin instantánea final y sin conservar respaldos automáticos.
2. **Probar la restauración de un respaldo** (antes de la defensa): descargar uno de `backups/`, cargarlo en una base
   vacía temporal dentro del servidor y comprobar que tenga los datos. No se debe tocar la base real.
3. **Cambiar el email del ADMIN** por uno real en Administración → Usuarios.
4. **Limpiar en el servidor:** `deploy/.env.antes-2.7.0` y `deploy/.env.dominio-anterior` (copias con permisos 600 de
   configuraciones previas). Borrarlas cuando no se necesite volver atrás.

### Modelo de IA (opción B, `docs/inferencia_remota.md`)
5. **Guía paso a paso para Juan: `docs/guia_modelo_juan.md`** (incluye al final la parte de Felipe). Estado: el
   servidor ya está en Tailscale. **Conectado el 11-11-2026:** PC de Juan `aurora-modelo` (`100.114.99.23`).
6. **Hecho (11-11-2026):** Tailscale con `aurora-ec2` (`100.83.18.31`) y `aurora-modelo` (`100.114.99.23`, Windows).
   `/health` responde 200 desde el host y desde el contenedor del backend (sin token, `/predict` da 401). Prueba de punta
   a punta con `HttpInferenceProvider` e imagen sintética (sin escribir en la base): `is_simulated=False`, una caja,
   **15 s** para 1,3 MB. La conexión va por relay DERP (São Paulo, ~190 ms), no directa: probablemente el firewall o
   el router de Juan bloquean UDP. Funciona; si se quiere más rapidez, revisar UDP 41641 en el PC de Juan.
   **Pendiente (Felipe):** confirmar que *Disable key expiry* quedó activo en `aurora-ec2` (y en `aurora-modelo`).
   **El día de la defensa:** PC de Juan encendido, sin suspensión, con Tailscale y el servicio arriba (ver la guía).
7. Si se quiere **todo en AWS:** `t4g.medium` + perfil `inference` (≈ USD 28 al mes), o Lambda. Detalle en la
   sección 5 de `docs/inferencia_remota.md`.

### Seguridad y cumplimiento
8. Ejecutar el **escaneo OWASP ZAP** (*Actions → ZAP baseline → Run workflow*) y revisar el informe.
9. **Historial de Session Manager:** contiene la contraseña temporal del ADMIN (ya reemplazada en el primer ingreso).
   Se puede borrar o dejar expirar.
10. **Rotar los secretos de la v1.0** en cada instalación local (`python -m scripts.rotate_secrets --db-password`).
11. Para **datos reales** (piloto): decidir la región (`us-east-2` con DPA, Chile con funciones avanzadas o
    instalación local), aceptar el DPA de AWS y revisar la lista de la sección 10 de `docs/despliegue_aws.md`.

### Orden y limpieza
12. Borrar la rama `claude/bold-maxwell-13fkwp` en GitHub (su contenido ya está en `main`):
    `git push origin --delete claude/bold-maxwell-13fkwp`.
13. Tags de versión desde un PC (desde las sesiones en la nube no se pueden subir tags):
    `git tag v2.6.0 9175cfe && git tag v2.7.0 2f5bbdc && git tag v2.8.0 43e0d1c && git tag v2.9.0 3bdaeb9 && git tag v2.9.1 85318b7 && git tag v2.9.2 d986618 && git push origin v2.6.0 v2.7.0 v2.8.0 v2.9.0 v2.9.1 v2.9.2`. Las imágenes ya se publicaron
    con `workflow_dispatch`.
14. Sacar del repositorio los pesos del modelo (≈63 MB) y llevarlos a un almacenamiento de artefactos.

### Dominio propio: `auroracare.cl` (listo; antes se pensó en `aurorahealth.cl`)
15. ~~Inscripción en NIC Chile~~: **hecha (11-11-2026), vence el 11-11-2027** (renovar en NIC antes de esa fecha).
    Servidores DNS: `ns-1350.awsdns-40.org`, `ns-862.awsdns-43.net`, `ns-73.awsdns-09.com`, `ns-1730.awsdns-24.co.uk`.
16. ~~Zona en Route 53~~: **hecha (11-11-2026).** Zona pública `auroracare.cl`, ID `Z0628464DNWEOT5ICYNC`
    (USD 0,50 al mes). Registro `A` `demo` → `13.184.207.158` (TTL 300).
17. ~~Apuntar el sitio~~: **hecho (11-11-2026).** En `deploy/.env`:
    `SITE_ADDRESS="demo.auroracare.cl, 13-184-207-158.sslip.io"` (Caddy saca certificado para las dos) y
    `PUBLIC_URL=https://demo.auroracare.cl`. Los valores anteriores quedaron en `deploy/.env.dominio-anterior`.
    Opcional: que sslip.io redirija al dominio (bloque extra en `deploy/Caddyfile`) o quitarla de `SITE_ADDRESS`.
18. **Marca:** antes de usar «Aurora Care» comercialmente, revisar en **INAPI** que no haya una marca igual en
    salud o software.

### Venta a varias instituciones (decisión del 11-11-2026, aún no implementado)
19. **Modelo elegido:** **una instancia por institución**, todo en **una cuenta de AWS del equipo** (cobran una
    mensualidad que incluye la infraestructura). Cada hospital: su EC2, base de datos, bucket, secretos y subdominio
    (`<hospital>.auroracare.cl`). Aislamiento total y **sin cambios al código**.
20. **Herramienta a construir: `aurora-admin`** (menú en terminal; plantilla de CloudFormation + script en Python).
    Opciones: inscribir institución (≈ 15 min: servidor, IP, bucket, rol, secretos en Parameter Store, registro DNS,
    instalación, respaldo y primer administrador), listar con estado, versión y costo (etiquetas por institución),
    actualizar una o todas, respaldar o restaurar, pausar o reactivar, y dar de baja exportando los datos. Más
    adelante, un panel web de superadministrador. Estimación: un par de días para la versión 1.
21. **Antes de vender:** el modelo de IA es un prototipo no validado y podría requerir registro como dispositivo
    médico en el **ISP**. Además: **contrato de encargo** con cada institución (ellos son responsables y el equipo es
    encargado del tratamiento), textos de consentimiento y reportes con el nombre de cada hospital, **salir del plan
    gratuito** (pruebas, vence en mayo) y definir soporte y SLA. Con muchos clientes, evaluar una cuenta de AWS por
    cliente.

## 3. Operación del servidor (comandos)

Entrar: EC2 → `aurora-prod` → **Conectar** → **Administrador de sesiones**. Luego:

```bash
sudo su - ec2-user
cd /opt/aurora
alias dc='docker compose -f docker-compose.yml -f deploy/docker-compose.prod.yml --env-file deploy/.env'
```

| Tarea | Comando |
|---|---|
| Estado | `dc ps` |
| Logs recientes | `dc logs --tail 100 backend` (o `web`, `db`). También en CloudWatch `/aurora/prod` |
| Actualizar a una versión nueva | `git pull`, cambiar `AURORA_VERSION` en `deploy/.env` por el tag de imagen publicado (`sha-…` o `vX.Y.Z`), `dc pull && dc up -d` (las migraciones se aplican solas) |
| Respaldo manual | `./deploy/backup_db.sh` |
| Último respaldo | `tail -3 /home/ec2-user/aurora-backup.log` |
| Reiniciar todo | `dc restart` |
| Apagar para ahorrar | Detener la instancia en la consola (siguen cobrándose el disco y la IP, ≈ USD 4 al mes) |

**Publicar imágenes nuevas:** en GitHub, *Actions → Publicar imágenes → Run workflow* (rama `main`), o un tag
`vX.Y.Z` subido desde un PC. Tarda unos 3 a 5 minutos; si la imagen `web` pasa de 15 minutos, algo está mal (antes de
`702bf84` el frontend se compilaba emulado y podía colgarse).

**Si el CI falla en «Imágenes Docker y prueba de humo» con `context deadline exceeded` al descargar `postgres`:** es
una falla pasajera del registro `public.ecr.aws`, no del código. Se resuelve con *Re-run jobs*.

## 4. Para agentes de Claude que continúen este trabajo

- **Acceso a AWS desde una sesión en la nube:** perfil `aurora` con `aws login --remote --region us-east-2 --profile aurora`.
  Se muestra un enlace, el usuario inicia sesión y pega el código. La sesión dura 12 horas y se renueva hasta 90 días,
  pero en una sesión nueva hay que repetirlo, porque el contenedor no conserva `~/.aws`. Hay que permitir
  `signin.aws.amazon.com` en la red del entorno.
- **Comandos en el servidor sin SSH:** SSM `SendCommand` (`AWS-RunShellScript`) sobre `i-0f7427c0dac2fd6b0`. Ojo: el
  historial de SSM guarda los parámetros, así que **nunca pasar secretos** en un comando ni leerlos para mostrarlos en
  el chat. Los secretos viven solo en `/opt/aurora/deploy/.env`.
- **Servidor MCP de AWS (`aws-mcp`):** a veces no conecta. Si no está, usar el AWS CLI con `--profile aurora`.
- **Commits:** en `main`, con la autoría de Felipe (la misma de los commits anteriores) y **sin coautoría de Claude**
  (pedido del equipo). Desde la nube no se pueden subir tags.
- **Imágenes Docker:** se bajan desde `public.ecr.aws` (Docker Hub limita las descargas). Para construirlas en el
  entorno en la nube hay que agregar el CA del proxy en una copia temporal del Dockerfile (ver `/root/.ccr/README.md`),
  nunca en el Dockerfile del repositorio.
- **Desplegar una versión (patrón usado el 11-11-2026):** commit en `main` → *Publicar imágenes* con
  `workflow_dispatch` (herramienta de GitHub `actions_run_trigger`) → respaldo (`./deploy/backup_db.sh`) si hay
  cambios de datos → por SSM, como `ec2-user`: esperar con `docker manifest inspect` a que existan
  `$AURORA_IMAGE_PREFIX-web:sha-…` y `-backend:sha-…`, `git pull --ff-only`, cambiar `AURORA_VERSION`,
  `dc pull backend web && dc up -d backend web`, y probar `https://demo.auroracare.cl/api/health` y el `<title>`.
  Un despliegue a producción necesita la confirmación explícita de Felipe en el chat (el modo automático lo bloquea).
- **El estado de SSM puede decir `Success` aunque el script falle:** el último comando (`rm -f`) define el estado.
  Leer siempre `StandardOutputContent` y `StandardErrorContent` (p. ej., `manifest unknown` = imagen aún no publicada).
- **Nivel de ayuda en AWS:** el usuario eligió **alto** (explicar cada paso, proponer alternativas y buenas
  prácticas).

## 5. Dónde está la documentación

- `docs/despliegue_aws.md`: guía completa (este despliegue sigue esa guía, opción de costo mínimo).
- `docs/inferencia_remota.md`: modelo en el PC de Juan con Tailscale y cómo moverlo a AWS.
- `docs/guia_modelo_juan.md`: pasos para Juan (y para Felipe) para conectar el modelo.
- `DESIGN.md` y `PRODUCT.md`: sistema visual (también lo usan los PDF, vía `src/utils/pdfTheme.ts`) y contexto de producto.
- `docs/cumplimiento_legal.md` y `docs/seguridad_owasp.md`: cumplimiento y seguridad.
- `docs/CHANGELOG_SPRINTS.md`: qué se hizo en cada versión.
