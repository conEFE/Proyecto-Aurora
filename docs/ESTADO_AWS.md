# Estado del despliegue en AWS y plan para continuar

Actualizado: 11-11-2026 (tarde). Versión desplegada: **2.9.1** (reportes PDF con el diseño de la interfaz) sobre la **2.9.0** («Aurora Care»: landing, sección Pacientes, un caso
por examen con varias imágenes, eliminar pacientes sin casos e informe de gestión en PDF), imágenes `sha-85318b7…` de
`main`. Sin migraciones nuevas desde la 2.6.0.

**Datos de demostración en producción (11-11-2026):** `python -m scripts.seed_demo` cargó 120 pacientes ficticios (RUT
desde 40.000.000) y 134 casos en 10 semanas, a nombre del médico de prueba. Respaldo previo:
`backups/aurora-20261111T145234Z.sql.gz` (restaurarlo para quitarlos; la auditoría no permite borrar).

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
| Modelo de IA | `INFERENCE_PROVIDER=simulated` por ahora. El token del modelo ya está en `deploy/.env` |
| Usuarios | ADMIN (Felipe, con email provisorio `admin@aurora-demo.cl`) y médico de prueba `11111111-1` (ficticio) |

**Costo estimado:** ≈ USD 11 al mes, descontados de los créditos (alcanza para todo el plan gratuito).

## 2. Plan para continuar

### Prioridad alta
1. **Actividad de RDS (+USD 20):** iniciarla desde *Earn AWS credits*. Usar **RDS PostgreSQL** (no Aurora),
   capa gratuita, `db.t4g.micro`, una zona, 20 GB sin autoescalado y sin acceso público. Cuando aparezca completada,
   **borrarla** sin instantánea final y sin conservar respaldos automáticos.
2. **Probar la restauración de un respaldo** (antes de la defensa): descargar uno de `backups/`, cargarlo en una base
   vacía temporal dentro del servidor y comprobar que tenga los datos. No se debe tocar la base real.
3. **Cambiar el email del ADMIN** por uno real en Administración → Usuarios.
4. ~~Diseño visual~~: **hecho y desplegado (2.7.0, 11-11-2026).** Modo claro rosado/blanco y oscuro morado/negro;
   sistema en `DESIGN.md`. Verificado en producción: `/theme-init.js` responde 200, el tema elegido se mantiene al
   recargar, la fuente Atkinson se sirve desde el propio sitio y la consola no muestra errores de CSP. Al publicarlo se
   corrigió el `Dockerfile` del sitio, que no copiaba `public/`. En el servidor quedó `deploy/.env.antes-2.7.0`, una
   copia de la configuración previa (con permisos 600): se puede borrar.

### Modelo de IA (opción B, `docs/inferencia_remota.md`)
5. **Guía paso a paso para Juan: `docs/guia_modelo_juan.md`** (incluye al final la parte de Felipe). Estado: guía
   entregada; **nada configurado todavía** (ni Tailscale ni el servicio en el PC de Juan).
6. **Hecho (11-11-2026):** red de Tailscale creada y servidor unido como `aurora-ec2` (`100.83.18.31`). Falta:
   desactivar la expiración de su llave (*Machines → ⋯ → Disable key expiry*), invitar a Juan y enviarle el token.
   Pasos originales: **Felipe:** crear la red de Tailscale (login.tailscale.com, con su Google o GitHub), **invitar a Juan**
   (*Users → Invite users*), unir el servidor (`curl -fsSL https://tailscale.com/install.sh | sh` y
   `sudo tailscale up --hostname aurora-ec2`) y enviarle a Juan el token por mensaje directo
   (`sudo grep '^INFERENCE_API_TOKEN=' /opt/aurora/deploy/.env | cut -d= -f2-`).
   **Cuando Juan avise:** en `deploy/.env`, `INFERENCE_PROVIDER=http` e `INFERENCE_URL=http://<IP 100.x de Juan>:8080`
   (la IP, no el nombre: dentro de los contenedores el nombre puede no resolverse), y `dc up -d`. Probar con
   `curl -H "Authorization: Bearer <token>" http://<IP>:8080/health` y subiendo una imagen ficticia.
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
    `git tag v2.6.0 9175cfe && git tag v2.7.0 2f5bbdc && git tag v2.8.0 43e0d1c && git tag v2.9.0 3bdaeb9 && git tag v2.9.1 85318b7 && git push origin v2.6.0 v2.7.0 v2.8.0 v2.9.0 v2.9.1`. Las imágenes ya se publicaron
    con `workflow_dispatch`.
14. Sacar del repositorio los pesos del modelo (≈63 MB) y llevarlos a un almacenamiento de artefactos.

### Dominio propio: `auroracare.cl` (en curso; antes se pensó en `aurorahealth.cl`)
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
`vX.Y.Z` subido desde un PC.

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
- **Nivel de ayuda en AWS:** el usuario eligió **alto** (explicar cada paso, proponer alternativas y buenas
  prácticas).

## 5. Dónde está la documentación

- `docs/despliegue_aws.md`: guía completa (este despliegue sigue esa guía, opción de costo mínimo).
- `docs/inferencia_remota.md`: modelo en el PC de Juan con Tailscale y cómo moverlo a AWS.
- `docs/guia_modelo_juan.md`: pasos para Juan (y para Felipe) para conectar el modelo.
- `DESIGN.md` y `PRODUCT.md`: sistema visual de la 2.7.0 y contexto de producto.
- `docs/cumplimiento_legal.md` y `docs/seguridad_owasp.md`: cumplimiento y seguridad.
- `docs/CHANGELOG_SPRINTS.md`: qué se hizo en cada versión.
