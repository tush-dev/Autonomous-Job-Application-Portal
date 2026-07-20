"""Initialize a fresh database, then use Alembic for subsequent upgrades."""

import asyncio

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.models import Base  # Imports every model and populates Base.metadata.


async def create_fresh_schema_if_needed() -> bool:
    engine = create_async_engine(str(settings.DATABASE_URL))
    try:
        async with engine.begin() as connection:
            tables = await connection.run_sync(
                lambda sync_connection: set(inspect(sync_connection).get_table_names())
            )
            application_tables = tables - {"alembic_version"}
            if application_tables:
                return False

            await connection.run_sync(Base.metadata.create_all)
            return True
    finally:
        await engine.dispose()


def main() -> None:
    alembic_config = Config("alembic.ini")
    if asyncio.run(create_fresh_schema_if_needed()):
        command.stamp(alembic_config, "head")
    else:
        command.upgrade(alembic_config, "head")


if __name__ == "__main__":
    main()
