#!/bin/sh
# Respaldo de PostgreSQL (opción con la base en contenedor) a S3, cifrado con SSE-KMS.
# Programarlo en el servidor, p. ej. todos los días a las 03:15:
#   15 3 * * * cd /opt/aurora && ./deploy/backup_db.sh >> /var/log/aurora-backup.log 2>&1
# Requiere: AWS CLI, rol de instancia con s3:PutObject y kms:GenerateDataKey, y BACKUP_BUCKET en deploy/.env.
# Con Amazon RDS no hace falta: use los respaldos automáticos de RDS.
set -eu
cd "$(dirname "$0")/.."
# Lee solo las variables necesarias (no ejecuta el archivo: los valores pueden tener espacios)
env_value() { grep -E "^$1=" deploy/.env | tail -1 | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//'; }
BACKUP_BUCKET=$(env_value BACKUP_BUCKET)
S3_KMS_KEY_ID=$(env_value S3_KMS_KEY_ID)
: "${BACKUP_BUCKET:?Defina BACKUP_BUCKET en deploy/.env}"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
file="/tmp/aurora-${stamp}.sql.gz"
trap 'rm -f "$file"' EXIT
docker compose exec -T db pg_dump -U aurora -d aurora --no-owner | gzip -9 > "$file"
extra=""
[ -n "${S3_KMS_KEY_ID:-}" ] && extra="--sse-kms-key-id ${S3_KMS_KEY_ID}"
# shellcheck disable=SC2086
aws s3 cp "$file" "s3://${BACKUP_BUCKET}/backups/aurora-${stamp}.sql.gz" --sse aws:kms $extra --only-show-errors
echo "Respaldo subido: backups/aurora-${stamp}.sql.gz"
