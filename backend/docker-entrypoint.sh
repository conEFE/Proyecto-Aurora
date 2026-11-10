#!/bin/sh
# Aplica las migraciones antes de iniciar la API (RUN_MIGRATIONS=false para desactivarlo).
set -e
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    echo "Aplicando migraciones (alembic upgrade head)..."
    tries=0
    until alembic upgrade head; do
        tries=$((tries + 1))
        if [ "$tries" -ge 10 ]; then
            echo "No se pudo conectar a la base de datos tras $tries intentos" >&2
            exit 1
        fi
        echo "Base de datos no disponible; reintento en 3 s ($tries/10)"
        sleep 3
    done
fi
exec "$@"
