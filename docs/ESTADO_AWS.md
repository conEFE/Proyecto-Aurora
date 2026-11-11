# Estado del despliegue en AWS y plan para continuar

Actualizado: 11-11-2026. Versión desplegada: **2.7.0** (rediseño visual «Orden de mamografía»), imágenes
`sha-2f5bbdc…` de `main`. El backend no cambió respecto de la 2.6.0.

## 1. Qué está funcionando

| Pieza | Detalle |
|---|---|
| Sitio | **https://13-184-207-158.sslip.io** (HTTPS de Let's Encrypt, renovación automática por Caddy) |
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
5. **Guía paso a paso para Juan: `docs/guia_modelo_juan.md`.** Juan instala **Tailscale** en su PC (nombre `aurora-modelo`) y levanta el servicio con
   `docker-compose.gpu.yml` o en forma nativa.
6. En el servidor: instalar Tailscale (`sudo tailscale up --hostname aurora-ec2`), poner en `deploy/.env`
   `INFERENCE_PROVIDER=http` e `INFERENCE_URL=http://aurora-modelo:8080`, y entregarle a Juan el
   `INFERENCE_API_TOKEN` por un canal privado (no por chat ni por el repositorio). Después, `dc up -d`.
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
13. Tag de versión: `git tag v2.6.0 9175cfe && git push origin v2.6.0` desde un PC (desde la sesión en la nube no se
    pudo subir tags). Las imágenes ya se publicaron con `workflow_dispatch`.
14. Sacar del repositorio los pesos del modelo (≈63 MB) y llevarlos a un almacenamiento de artefactos.

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

## 4. Dónde está la documentación

- `docs/despliegue_aws.md`: guía completa (este despliegue sigue esa guía, opción de costo mínimo).
- `docs/inferencia_remota.md`: modelo en el PC de Juan con Tailscale y cómo moverlo a AWS.
- `docs/cumplimiento_legal.md` y `docs/seguridad_owasp.md`: cumplimiento y seguridad.
- `docs/CHANGELOG_SPRINTS.md`: qué se hizo en cada versión.
