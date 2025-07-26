import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.database.models import Base
import os
from dotenv import load_dotenv

# Загрузить переменные окружения
load_dotenv()

# ⛳️ ВАЖНО: config должен быть объявлен ДО использования
config = context.config
config.set_main_option('sqlalchemy.url', os.getenv("SYNC_DB_URL"))

# Настройки логирования Alembic (необязательно)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные моделей для автогенерации
target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=os.environ["DB_URL"],  # тут можно оставить async URL для генерации sql-файлов
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda conn: context.configure(
                connection=conn,
                target_metadata=target_metadata,
                compare_type=True,
            )
        )
        async with connection.begin():
            await connection.run_sync(context.run_migrations)


def run():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())


run()
