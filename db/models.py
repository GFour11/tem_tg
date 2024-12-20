import os
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_FROM_URL').replace('postgresql', 'postgresql+asyncpg')
#DATABASE = f"postgresql+asyncpg://os.get{DB_USER}:os.get{DB_PASSWORD}@os.get{DB_HOST}:os.get{DB_PORT}/os.get{DB_NAME}}"

engine = create_async_engine(DATABASE_URL, echo=True)


Base = declarative_base()


class User(Base):
    __tablename__ = 'users_tg'  # Назва таблиці в базі даних

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=True, unique=False)
    user_id = Column(String(50), nullable=True, unique=False)
    phone = Column(String(50), nullable=True)
    code_short = Column(String(50), nullable=True)
    code_long = Column(String(150), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Таблиці створені.")


async def main():
    await create_tables()


if __name__ == "__main__":

    asyncio.run(main())
