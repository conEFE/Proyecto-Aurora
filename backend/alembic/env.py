import sys
import os
from logging.config import fileConfig
from urllib.parse import quote_plus

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from dotenv import load_dotenv

# Cargar variables .env con codificación UTF-8 explícita
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path, encoding='utf-8')

# Importar models y Base
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.db.base import Base
from app.db.models.user import User
from app.db.models.case import Case
from app.db.models.image import Image

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Aquí debe estar tu metadata
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = os.getenv("DB_DSN")  # leer DB desde .env
    if not url:
        raise ValueError("DB_DSN no encontrado en variables de entorno")
    # Asegurar que la URL esté en formato string correcto
    if isinstance(url, bytes):
        url = url.decode('utf-8')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    db_dsn = os.getenv("DB_DSN")
    if not db_dsn:
        raise ValueError("DB_DSN no encontrado en variables de entorno")
    # Asegurar que el DSN esté en formato string correcto
    if isinstance(db_dsn, bytes):
        db_dsn = db_dsn.decode('utf-8')
    configuration["sqlalchemy.url"] = db_dsn  # usar .env

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()