import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE = os.getenv('DATABASE_FROM_URL').replace('postgresql', 'postgresql+asyncpg')
#DATABASE = f"postgresql+asyncpg://os.get{DB_USER}:os.get{DB_PASSWORD}@os.get{DB_HOST}:os.get{DB_PORT}/os.get{DB_NAME}}"

engine = create_async_engine(DATABASE)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    """yield database connection"""
    try:
        async with async_session() as session:
            yield session
    finally:
        await session.close()