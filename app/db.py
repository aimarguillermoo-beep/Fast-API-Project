from collections.abc import AsyncGenerator
import uuid
import datetime
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

class Post(Base):
    __tablename__ = "posts"
    
    # Usamos String para el ID en SQLite para evitar errores de tipo UUID
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    # Corregido a 'created_at' para que coincida con tu main.py
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

engine = create_async_engine(DATABASE_URL)

# Instancia del creador de sesiones
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    # IMPORTANTE: Usamos la factoría que ya tiene el engine configurado
    async with async_session_factory() as session:
        yield session
        # No es estrictamente necesario el close manual aquí porque el 'with' lo hacefrom collections.abc import AsyncGenerator
import uuid
import datetime
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

class Post(Base):
    __tablename__ = "posts"
    
    # Usamos String para el ID en SQLite para evitar problemas de compatibilidad con el tipo UUID nativo
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    # Importante: se llama 'created_at' con "d" para que coincida con tu main.py
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

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