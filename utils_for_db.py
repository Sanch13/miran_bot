import logging
import aiosqlite

from config import settings
from logging_config import logger


async def create_db():
    logger.info("Создание или верификация БД.")
    async with aiosqlite.connect(settings.DATABASE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                full_name TEXT,
                lottery_number INTEGER,
                status BOOLEAN,
                fio TEXT
                )
        ''')
        await db.commit()
    logger.info("Успешная создание или верификация БД.")


async def add_user(user_id: int, full_name: str, status: bool, fio: str):
    logger.info(f"Добавление пользователя ({fio}) с id {user_id}  в БД.")
    async with aiosqlite.connect(settings.DATABASE) as db:
        try:
            cursor = await db.execute('''SELECT COUNT(*) FROM users''')
            lottery_number = (await cursor.fetchone())[0] + 100
            await db.execute("""INSERT INTO users (user_id, full_name, lottery_number, status, fio)
                                VALUES (?, ?, ?, ?, ?)""", (user_id, full_name, lottery_number, status, fio))
            await db.commit()
        except aiosqlite.IntegrityError:
            logging.error(f"Пользователь ({fio}) с id {user_id} уже есть в БД.")
    logger.info(f"Пользователь ({fio}) с id {user_id} успешно добавлен в БД с лотерейным номером {lottery_number}.")


async def user_exists(user_id: int) -> bool:
    logger.info(f"Проверка пользователя с id {user_id} в БД.")
    async with aiosqlite.connect(settings.DATABASE) as db:
        sql: str = """SELECT 1 FROM users WHERE user_id = ?"""
        cursor = await db.execute(sql, (user_id,))
        exists = await cursor.fetchone() is not None
    logger.info(f"Пользователь с id {user_id} существует: {exists}")
    return exists


async def get_user_number(user_id: int) -> int:
    logger.info(f"Получаю лотерейный номер из БД для пользователя с id {user_id}.")
    async with aiosqlite.connect(settings.DATABASE) as db:
        sql: str = """SELECT lottery_number FROM users WHERE user_id = ?"""
        cursor = await db.execute(sql, (user_id,))
        result = await cursor.fetchone()
    logger.info(f"Лотерейный номер для пользователя с id {user_id}: {result[0] if result else 'None'}")
    return result[0] if result else None


async def get_list_participants():
    logger.info("Получение списка участников")
    sql: str = """SELECT lottery_number, fio FROM users"""
    async with aiosqlite.connect(settings.DATABASE) as db:
        cursor = await db.execute(sql)
        result = await cursor.fetchall()
    logger.info("Список участников получен")
    return result if result else None
