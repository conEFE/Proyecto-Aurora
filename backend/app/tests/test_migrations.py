from alembic import command
from sqlalchemy import inspect

from app.deps import engine
from app.tests.conftest import alembic_config


def test_downgrade_to_base_and_upgrade_to_head():
    """Toda migración debe ser reversible: base -> head -> base -> head."""
    cfg = alembic_config()
    command.downgrade(cfg, "base")
    tables = set(inspect(engine).get_table_names()) - {"alembic_version"}
    assert tables == set()
    command.upgrade(cfg, "head")
    assert {"users", "patients", "cases", "images", "inference_results"} <= set(
        inspect(engine).get_table_names()
    )
