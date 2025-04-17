import asyncio
import logging
import sys
import os
import json
from datetime import datetime, timedelta
import aiohttp
from aiogram import Bot, Dispatcher, html, Router, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters.command import CommandObject
import shelve
import gspread
import re
from google.oauth2.service_account import Credentials
from openai import AsyncOpenAI
from datetime import datetime
from zoneinfo import ZoneInfo

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_chatgpt_response(prompt: str) -> str:
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7  
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        return "Извините, не удалось обработать запрос"  
    


async def get_google_sheet_data(sheet_id: str, range_name: str = "B2:AB2"):
    scope = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    
    creds = Credentials.from_service_account_info({
        "type": os.getenv("GS_TYPE"),
        "project_id": os.getenv("GS_PROJECT_ID"),
        "private_key_id": os.getenv("GS_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GS_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("GS_CLIENT_EMAIL"),
        "client_id": os.getenv("GS_CLIENT_ID"),
        "auth_uri": os.getenv("GS_AUTH_URI"),
        "token_uri": os.getenv("GS_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GS_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("GS_CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("UNIVERSE_DOMAIN")
    }, scopes=scope)
    
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).get_worksheet(1) 
    data = sheet.get(range_name)
    return data


async def get_google_sheet(sheet_id, list_index):
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info({
        "type": os.getenv("GS_TYPE"),
        "project_id": os.getenv("GS_PROJECT_ID"),
        "private_key_id": os.getenv("GS_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GS_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("GS_CLIENT_EMAIL"),
        "client_id": os.getenv("GS_CLIENT_ID"),
        "auth_uri": os.getenv("GS_AUTH_URI"),
        "token_uri": os.getenv("GS_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GS_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("GS_CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("UNIVERSE_DOMAIN")
    }, scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id).get_worksheet(list_index) 






async def write_to_google_sheet(
    sheet_id: str,
    username: str,
    first_name: str,
    status: str,
    gpt_response: str
) -> bool:
    """
    Записывает данные в Google Sheets
    
    :param sheet_id: ID таблицы
    :param username: @username пользователя
    :param first_name: Имя пользователя
    :param status: Один из вариантов: 'Начал чат-бота', 'Собеседование', 'Отказ'
    :param gpt_response: Ответ от GPT
    :return: True если запись успешна, False при ошибке
    """
    try:
        # Получаем текущую дату
        tz = ZoneInfo('Europe/Moscow')
        current_date = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        
        # Подготовка данных для записи
        row_data = [
            current_date,          # Столбец A (дата)
            f"@{username}",        # Столбец B (@ник)
            first_name,            # Столбец C (имя)
            status,                # Столбец D (статус)
            "", "", "", "", "",    # Пустые столбцы E-J
            gpt_response          # Столбец K (ответ GPT)
        ]
        
        # Асинхронная запись
        loop = asyncio.get_event_loop()
        sheet = await loop.run_in_executor(None, get_google_sheet, sheet_id, 2)
        await loop.run_in_executor(None, sheet.append_row, row_data)
        
        return True
    except Exception as e:
        print(f"Ошибка записи в Google Sheets: {e}")
        return False



async def check_empty_cells(sheet_id: str) -> InlineKeyboardMarkup | None:
    """
    Проверяет наличие пустых ячеек в столбцах дат (B2:K2 - даты, B4:K21 - данные)
    и создает кнопки для столбцов с пустыми ячейками
    """
    try:
        # Получаем объект таблицы
        sheet = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: get_google_sheet(sheet_id, 0)
        )
        
        # 1. Получаем заголовки (даты из строки 2)
        dates = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: sheet.row_values(2)[1:11]  # B2:K2
        )
        
        # 2. Получаем данные (B4:K21)
        data = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: sheet.get('B4:K21')
        )
        
        print(f"Заголовки дат: {dates}")  # Отладочный вывод
        print(f"Получено строк данных: {len(data)}")  # Отладочный вывод
        
        keyboard = []
        
        # Проверяем каждый столбец (B-K)
        for col_idx in range(len(dates)):
            col_letter = chr(66 + col_idx)  # B=66, C=67,... K=75
            has_empty = False
            
            # Проверяем ячейки в столбце (18 строк)
            for row_idx in range(min(len(data), 18)):  # Защита от выхода за границы
                if len(data[row_idx]) <= col_idx or data[row_idx][col_idx] == '':
                    has_empty = True
                    break
            
            if has_empty:
                date = dates[col_idx] if col_idx < len(dates) else f"Столбец {col_letter}"
                keyboard.append([
                    InlineKeyboardButton(
                        text=date,
                        callback_data=f"select_date_{col_letter}2"  # Например "B2"
                    )
                ])
                print(f"Добавлена кнопка для {col_letter}")  # Отладочный вывод
        
        print(f"Создано кнопок: {len(keyboard)}")  # Отладочный вывод
        return InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None
        
    except Exception as e:
        print(f"Ошибка в check_empty_cells: {str(e)}", exc_info=True)
        return None




async def get_available_times(sheet_id: str, selected_date_cell: str) -> InlineKeyboardMarkup | None:
    """
    Проверяет доступное время в выбранном столбце даты
    
    :param sheet_id: ID Google-таблицы
    :param selected_date_cell: Ячейка с выбранной датой (например "B2")
    :return: Клавиатура с доступным временем или None, если нет свободных слотов
    """
    try:
        # Получаем букву столбца из выбранной ячейки (например "B" из "B2")
        column_letter = selected_date_cell[0].upper()
        
        # Получаем диапазон времени (A4:A21) и выбранного столбца (B4:B21)
        time_range = f"A4:A21"
        date_range = f"{column_letter}4:{column_letter}21"
        
        # Получаем данные из таблицы
        sheet = get_google_sheet(sheet_id, 0)
        
        # Читаем данные асинхронно
        loop = asyncio.get_event_loop()
        time_values = await loop.run_in_executor(None, lambda: sheet.range(time_range))
        date_values = await loop.run_in_executor(None, lambda: sheet.range(date_range))
        
        # Создаем клавиатуру с доступным временем
        keyboard = []
        
        for time_cell, date_cell in zip(time_values, date_values):
            # Если ячейка времени не пустая и ячейка даты пустая
            if time_cell.value and not date_cell.value:
                keyboard.append([
                    InlineKeyboardButton(
                        text=time_cell.value,
                        callback_data=f"select_time_{column_letter}_{time_cell.row}"
                    )
                ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None
        
    except Exception as e:
        print(f"Ошибка при проверке доступного времени: {e}")
        return None



