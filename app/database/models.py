import os
import ssl
from dotenv import load_dotenv

from sqlalchemy import ForeignKey, String, BigInteger, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

load_dotenv()

DB_URL = os.getenv('DATABASE_URL')
if DB_URL and '?' in DB_URL:
    DB_URL = DB_URL.split('?')[0]  # Убираем параметры после '?'

# Переменные для engine и session
engine = None
async_session = None


def init_database():
    global engine, async_session

    try:
        # Пытаемся подключиться к основной БД
        engine = create_async_engine(
            url=DB_URL,
            echo=True,
            connect_args={
                "ssl": "require"  # Указываем требование SSL
            }
        )
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        print("✅ Main database initialized")
    except Exception as e:
        print(f"❌ Main database failed: {e}")
        # Если основная БД недоступна, используем SQLite fallback
        engine = create_async_engine('sqlite+aiosqlite:///fallback.db', echo=True)
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        print("✅ Fallback SQLite database initialized")


# Инициализируем базу данных при импорте модуля
init_database()

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id = mapped_column(BigInteger)


class WorkTasks(Base):
    __tablename__ = 'worktasks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    name: Mapped[str] = mapped_column(String(50))

    items: Mapped[list['WorkTaskItem']] = relationship("WorkTaskItem", back_populates="task",
                                                       cascade="all, delete-orphan")


class WorkTaskItem(Base):
    __tablename__ = 'worktask_items'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category: Mapped[int] = mapped_column(ForeignKey('worktasks.id'))
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(512))
    photo: Mapped[str] = mapped_column(String(512))
    status: Mapped[bool] = mapped_column(Boolean, default=False)

    task: Mapped['WorkTasks'] = relationship("WorkTasks", back_populates="items")


async def async_main():
    try:
        if engine is None:
            init_database()

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Database error: {e}")