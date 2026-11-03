import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path, encoding="utf-8")
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import app.db.models  # noqa: E402,F401  (registra todos los modelos en el metadata)
from app.db.base import Base  # noqa: E402

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def _dsn() -> str:
    # Los tests pasan la URL por config.attributes sin tocar el entorno
    url = config.attributes.get("db_dsn") or os.getenv("DB_DSN")
    if not url:
        raise ValueError("DB_DSN no encontrado en variables de entorno")
    return url


def run_migrations_offline() -> None:
    context.configure(
        url=_dsn(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = _dsn()
    connectable = engine_from_config(configuration, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
