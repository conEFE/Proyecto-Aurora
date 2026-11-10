# API de Proyecto Aurora (FastAPI). Imágenes base desde el espejo público de AWS (sin límite de Docker Hub).
FROM public.ecr.aws/docker/library/python:3.12.16-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependencias primero (capa reutilizable entre builds)
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY alembic.ini init_db.py init_user.py generate_key.py ./
COPY alembic ./alembic
COPY app ./app
COPY scripts ./scripts
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

# Usuario sin privilegios; las imágenes locales (STORAGE_BACKEND=local) van en /data
RUN useradd --system --uid 10001 --home /app aurora \
    && mkdir -p /data/images \
    && chown -R aurora:aurora /data \
    && rm -rf app/tests \
    && chmod 0755 /usr/local/bin/docker-entrypoint.sh
USER aurora

ENV FILES_DIR=/data/images \
    ENABLE_API_DOCS=false \
    TRUST_PROXY_HEADERS=true

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status == 200 else 1)"

ENTRYPOINT ["docker-entrypoint.sh"]
# ROOT_PATH=/api: la API se publica detrás del proxy en /api (los enlaces de /docs lo consideran)
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --root-path \"${ROOT_PATH:-}\" --workers \"${WEB_CONCURRENCY:-2}\" --no-server-header"]
