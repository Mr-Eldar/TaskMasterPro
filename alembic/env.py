from logging.config import fileConfig
import os
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.database.models import Base  # путь к твоим моделям

load_dotenv()

# config
config = context.config
fileConfig(config.config_file_name)

# Загружаем URL БД из переменной окружения
db_url = os.getenv("SYNC_DB_URL")
config.set_main_option("sqlalchemy.url", db_url)

# Основная логика Alembic
def run_migrations_offline():
    context.configure(
        url=db_url,
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()