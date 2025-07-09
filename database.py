import asyncpg
import os
from typing import AsyncIterator

DB_HOST = os.getenv("DB_HOST")          
DB_PORT = os.getenv("DB_PORT")          
DB_NAME = os.getenv("DB_NAME")          
DB_USER = os.getenv("DB_USER")          
DB_PASSWORD = os.getenv("DB_PASSWORD")  

async def get_async_connection() -> AsyncIterator[asyncpg.Pool]:
    """Создает и возвращает пул подключений к PostgreSQL."""
    try:
        pool = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST,
            port=DB_PORT,
            min_size=1,
            max_size=10,
            timeout=30
        )
        print("✅ Подключение к PostgreSQL установлено")
        return pool
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
        raise

async def save_action_to_db(
    pool: asyncpg.Pool,
    column_letter: str,
    row_number: int,
    candidate_chat_id: int,
    sheet_id: str,
    sheet_range: str,
    decline_text: str = None,
    learn_text: str = None,
    practice_text: str = None,
    accept_text: str = None
) -> int:
    """Сохраняет данные действия в БД и возвращает action_id"""
    async with pool.acquire() as conn:
        return await conn.fetchval(
            """
            INSERT INTO candidate_actions (
                column_letter, row_number,
                candidate_chat_id, sheet_id,
                sheet_range, decline_text,
                learn_text, practice_text, accept_text
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING action_id
            """,
            column_letter, row_number,
            candidate_chat_id, sheet_id,
            sheet_range, decline_text,
            learn_text, practice_text, accept_text
        )
