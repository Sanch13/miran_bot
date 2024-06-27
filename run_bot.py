import asyncio

from init_bot import dp, bot
from utils_for_db import create_db
from logging_config import logger
import handlers


async def main():
    logger.info("Запуск бота...")

    await create_db()
    logger.info("База данных создана или верифицирована.")

    await dp.start_polling(bot)
    logger.info("Polling started.")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Выход")
    except Exception as error:
        logger.exception("Exception occurred: {}", error)
