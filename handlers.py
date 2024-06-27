import random

from aiogram import types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

from middleware import check_subscribe, is_user_admin
from init_bot import bot, router
from utils_for_db import add_user, user_exists, get_user_number, get_list_participants
from logging_config import logger
from config import settings


class Registration(StatesGroup):
    fio = State()


def get_inline_keyboard(is_admin: bool) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="Нужна Алиса",
                                 callback_data="participate"),
            InlineKeyboardButton(text="Узнать свой номер",
                                 callback_data="get_number")
        ]
    ]

    if is_admin:
        buttons.append(
            [
                InlineKeyboardButton(text="Получить список участников", callback_data="admin_action"),
                InlineKeyboardButton(text="Узнать победителя", callback_data="get_random_number")
            ]
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


@router.callback_query(lambda c: c.data == "participate")
@check_subscribe
async def participate_callback(callback_query: CallbackQuery, state: FSMContext, *args, **kwargs):
    user_id = callback_query.from_user.id

    if await user_exists(user_id):
        user_number = await get_user_number(user_id)
        await callback_query.answer('')
        await bot.send_message(user_id, f"Вы уже участвуете в лотерее под номером {user_number}")
        logger.info(f"Зарегестрированный пользователь {user_id} с номером {user_number} нажал на кнопку 'Участвовать в розыгрыше'.")
    else:
        await state.set_state(Registration.fio)
        await callback_query.message.answer(
            "Введите ваше ФИО",
        )
        await callback_query.answer()


@router.message(Registration.fio)
async def process_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    full_name = message.from_user.full_name or "Неизвестный пользователь"
    fio = message.text.strip()

    await add_user(user_id, full_name, status=True, fio=fio)
    user_number = await get_user_number(user_id)
    await message.answer(f"Вы участвуете в лотерее под номером {user_number}")
    logger.info(f"Пользователь {fio} с id {user_id} добавлен в БД с лотерейным номером {user_number}.")

    await state.clear()


@router.callback_query(lambda c: c.data == "get_number")
@check_subscribe
async def get_number_callback(callback_query: types.CallbackQuery, *args, **kwargs):
    user_id = callback_query.from_user.id

    user_number = await get_user_number(user_id)
    if user_number:
        await bot.send_message(user_id, f"Ваш номер: {user_number}")
        logger.info(f"Пользователь с id {user_id} запросил свой лотерейный номер {user_number}.")
    else:
        await bot.send_message(user_id, "Вы пока не участвуете в лотерее.")

    await callback_query.answer()


@router.callback_query(lambda c: c.data == "admin_action")
async def process_admin_action(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if await is_user_admin(bot, settings.CHANNEL_ID_TEST_CHANNEL_MIRAN, user_id):
        result = await get_list_participants()

        if result is None:
            await bot.send_message(user_id, "База даных пуста")
        else:
            total = len(result)
            all_numbers_participants = f"[{result[0][0]} - {result[-1][0]}]"
            data = f"Всего участников: {total}  \nУчаствуют номера: {all_numbers_participants}\n"
            text_result = ''.join(f"{item[0]} - {item[1]}\n" for item in result)
            await bot.send_message(user_id, data + text_result)

    await callback_query.answer()


@router.callback_query(lambda c: c.data == "get_random_number")
async def get_random_number_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    result = await get_list_participants()

    if result is None:
        await bot.send_message(user_id, "База даных пуста")
    else:
        logger.info(f"Определение случайного номера")
        number, fio = random.choice(result)
        logger.info(f"Победитель {fio} с номером {number}")
        answer_text = f"Победитель {fio} с номером {number}"
        await bot.send_message(user_id, answer_text)
    await callback_query.answer()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"Пользователь {message.from_user.full_name} с id {message.from_user.id} нажал кнопку /start.")
    is_admin = await is_user_admin(bot, settings.CHANNEL_ID_TEST_CHANNEL_MIRAN, user_id)
    keyboard = get_inline_keyboard(is_admin=is_admin)
    await message.answer(text="""Выберите одно из двух действии.\nЧтобы участвовать в розыгрыше Алисы нажмите на 'Участвовать в розыгрыше' и вам присвоят номер. \nЧтобы узнать свой номер участия нажмите на 'Узнать свой номер'.""", reply_markup=keyboard)
