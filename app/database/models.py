from sqlalchemy import ForeignKey, String, BigInteger, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


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