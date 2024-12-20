import os
from db.models import User
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from db.db_conn import get_db

path = os.getcwd()

async def create_user(username, user_id):
    async for session in get_db():
        async with session.begin():
            new_user = User(username=username, user_id=user_id)
            session.add(new_user)
            await session.commit()
            print(f"Користувач із user_id {user_id} створений.")
            return new_user


async def check_user_exists(user_id):
    async for session in get_db():
        async with session.begin():
            try:

                result = await session.execute(select(User).where(User.user_id == user_id))
                user = result.scalar_one()
                if user:
                    print(f"Користувач із user_id {user_id} існує.")
                    return user
                else:
                    return False

            except NoResultFound:
                print(f"Користувача з user_id {user_id} не знайдено.")
                return False


async def update_user_phone(user_id, phone):
    async for session in get_db():
        async with session.begin():
            try:
                result = await session.execute(select(User).where(User.user_id == user_id))
                user = result.scalar_one()

                user.phone = phone
                await session.commit()
                print(f"Телефон {phone} збережено для user_id {user_id}.")
                return user

            except NoResultFound:
                print(f"Користувача з user_id {user_id} не знайдено.")
                return None


async def update_user_code_short(user_id, code):
    async for session in get_db():
        async with session.begin():
            try:
                result = await session.execute(select(User).where(User.user_id == user_id))
                user = result.scalar_one()

                user.code_short = code
                await session.commit()
                print(f"Телефон {code} збережено для user_id {user_id}.")
                return user

            except NoResultFound:
                print(f"Користувача з user_id {user_id} не знайдено.")
                return None


async def update_user_code_long(user_id, code):
    async for session in get_db():
        async with session.begin():
            try:
                result = await session.execute(select(User).where(User.user_id == user_id))
                user = result.scalar_one()

                user.code_long = code
                await session.commit()
                print(f"Телефон {code} збережено для user_id {user_id}.")
                return user

            except NoResultFound:
                print(f"Користувача з user_id {user_id} не знайдено.")
                return None