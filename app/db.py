from collections.abc import AsyncGenerator
import uuid
import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from fastapi_users.db import SQLAlchemyBaseUserTableUUID


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Usuario del sistema con autenticación"""
    posts = relationship("Post", back_populates="owner")


DATABASE_URL = "sqlite+aiosqlite:///./test.db"


class Post(Base):
    __tablename__ = "posts"

    # Usamos String para el ID en SQLite para evitar errores de tipo UUID
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relación con el usuario propietario
    owner = relationship("User", back_populates="posts")


engine = create_async_engine(DATABASE_URL)

# Creamos la factoría vinculada al motor
async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def create_db_and_tables():
    async with engine.begin() as conn:
        # Esto crea las tablas en el archivo test.db
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    # Usamos la factoría para generar la sesión
    async with async_session_factory() as session:
        yield session
