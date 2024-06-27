from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import settings
from init_bot import bot, Bot
from logging_config import logger


def check_subscribe(func):
    """Checking user subscribing on the group or channel"""
    async def wrapper(message: Message, state: FSMContext):
        user_full_name = message.from_user.full_name
        user_id = message.from_user.id
        logger.info(f"Проверка подписки с id {user_id} для ({user_full_name}).")
        status = await bot.get_chat_member(chat_id=settings.CHANNEL_ID_TEST_CHANNEL_MIRAN, user_id=user_id)
        if status.status in ('member', 'creator', 'administrator'):
            logger.info(f"Пользователь {user_full_name} с id {user_id} подписан.")
            await func(message, state)
        else:
            text = f"Привет, {user_full_name or ''}." \
                   f"\nВы не подписаны на телеграм-канал  {settings.CHANNEL_LINK}." \
                   f"\nЧтобы пользоваться ботом подпишитесь!!!"
            logger.info(f"Пользователь {user_full_name} с id {user_id} не подписан.")
            await message.answer('')
            await bot.send_message(user_id, text=text)
    return wrapper


async def is_user_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    member = await bot.get_chat_member(chat_id, user_id)
    return member.status in ['administrator', 'creator']
