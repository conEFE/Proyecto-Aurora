#!/bin/bash
# Respaldo de PostgreSQL a S3, cifrado con SSE-KMS. Sirve con la base en contenedor y con Amazon RDS.
# Se programa en el servidor (crontab de ec2-user), p. ej. todos los días a las 03:15 hora de Chile:
#   CRON_TZ=America/Santiago
#   15 3 * * * cd /opt/aurora && ./deploy/backup_db.sh >> /home/ec2-user/aurora-backup.log 2>&1
# Requiere: AWS CLI, rol de instancia con s3:PutObject en backups/*, y BACKUP_BUCKET en deploy/.env.
# Con Amazon RDS (DB_DSN definido en deploy/.env) el volcado se hace desde un contenedor efímero de PostgreSQL 16;
# complementa los respaldos automáticos de RDS, que en el plan gratuito duran solo 1 día.
#
# Falla (código distinto de 0, sin subir nada) si pg_dump falla o el respaldo queda incompleto.
set -euo pipefail
cd "$(dirname "$0")/.."

# Lee solo las variables necesarias (no ejecuta el archivo: los valores pueden tener espacios)
env_value() { grep -E "^$1=" deploy/.env | tail -1 | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//' || true; }
BACKUP_BUCKET=$(env_value BACKUP_BUCKET)
DB_DSN=$(env_value DB_DSN)
S3_KMS_KEY_ID=$(env_value S3_KMS_KEY_ID)
: "${BACKUP_BUCKET:?Defina BACKUP_BUCKET en deploy/.env}"

# Mismos archivos que el despliegue: sin --env-file, Compose no resuelve las variables de deploy/.env
compose=(docker compose -f docker-compose.yml)
[ -f deploy/docker-compose.prod.yml ] && compose+=(-f deploy/docker-compose.prod.yml)
compose+=(--env-file deploy/.env)

stamp=$(date -u +%Y%m%dT%H%M%SZ)
file=$(mktemp "/tmp/aurora-${stamp}-XXXX.sql.gz")
trap 'rm -f "$file"' EXIT

if [ -n "${DB_DSN:-}" ]; then
    # Base en Amazon RDS. La URL va por variable de entorno (no queda en la lista de procesos) y sin el
    # sufijo +psycopg2 de SQLAlchemy, que libpq no entiende.
    PGURL="${DB_DSN/postgresql+psycopg2:/postgresql:}" docker run --rm -e PGURL \
        public.ecr.aws/docker/library/postgres:16-alpine sh -c 'pg_dump "$PGURL" --no-owner' | gzip -9 > "$file"
else
    "${compose[@]}" exec -T db pg_dump -U aurora -d aurora --no-owner | gzip -9 > "$file"
fi

# Un volcado completo de pg_dump termina con esta marca; si no está, el respaldo no sirve
if ! gzip -dc "$file" | tail -n 5 | grep -q "PostgreSQL database dump complete"; then
    echo "ERROR: el respaldo quedó incompleto; no se sube" >&2
    exit 1
fi

sse=(--sse aws:kms)
if [ -n "${S3_KMS_KEY_ID:-}" ]; then
    sse+=(--sse-kms-key-id "$S3_KMS_KEY_ID")
fi
aws s3 cp "$file" "s3://${BACKUP_BUCKET}/backups/aurora-${stamp}.sql.gz" "${sse[@]}" --only-show-errors
echo "$(date -u +%FT%TZ) Respaldo subido: backups/aurora-${stamp}.sql.gz ($(stat -c %s "$file") bytes)"
