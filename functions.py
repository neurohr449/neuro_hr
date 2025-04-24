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

from main import MOSCOW_TZ

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


async def get_google_sheet(sheet_id: str, list_index: int):
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    
    # Создаем credentials
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
    
    try:
        # Асинхронная авторизация
        client = await asyncio.to_thread(gspread.authorize, creds)
        
        # Асинхронное открытие таблицы и листа
        spreadsheet = await asyncio.to_thread(client.open_by_key, sheet_id)
        worksheet = await asyncio.to_thread(spreadsheet.get_worksheet, list_index)
        return worksheet
    except Exception as e:
        print(f"Ошибка доступа к Google Sheets: {e}")
        raise






async def write_to_google_sheet(
    sheet_id: str,
    username: str,
    first_name: str = None,
    status: str = None,
    gpt_response: str = None,
    full_name: str = None,
    phone_number: str = None,
    resume_link: str = None,
    interview_date: str = None,
    interview_time: str = None,
    qa_data: str = None
) -> bool:
    """
    Записывает или обновляет данные в Google Sheets с сохранением информации при отказе
    
    :param sheet_id: ID таблицы
    :param username: @username пользователя (обязательный параметр)
    :param first_name: Имя пользователя в Telegram
    :param status: Один из вариантов: 'Начал чат-бота', 'Собеседование', 'Отказ'
    :param gpt_response: Комментарий AI (столбец K)
    :param full_name: ФИО (столбец F)
    :param phone_number: Номер телефона (столбец G)
    :param resume_link: Ссылка на резюме (столбец H)
    :param interview_date: Дата собеседования (столбец I)
    :param interview_time: Время собеседования (столбец J)
    :param qa_data: Вопросы и ответы (столбец L)
    :return: True если запись успешна, False при ошибке
    """
    try:
        # Проверка обязательного поля username
        if not username:
            print("Ошибка: username обязателен")
            return False

        tz = ZoneInfo('Europe/Moscow')
        now = datetime.now(tz)
        current_date = now.strftime("%Y-%m-%d %H:%M:%S")
        current_day = now.strftime("%d")
        current_month = now.strftime("%m")
        current_year = now.strftime("%Y")
        
        # Получаем данные из таблицы
        sheet = await get_google_sheet(sheet_id, 2)
        data = await asyncio.to_thread(sheet.get_all_records)
        
        # Проверяем, есть ли пользователь уже в таблице
        user_row = None
        for i, row in enumerate(data, start=2):  # начинаем с 2, так как первая строка - заголовки
            if f"@{username}".lower() == row.get('ТГ', '').lower():
                user_row = i
                break
        
        # Блокируем изменения только если статус уже "Отказ" И мы не пытаемся его обновить
        if user_row and data[user_row-2].get('Статус') == "Отказ" and status != "Отказ":
            return False
        
        # Подготовка данных для обновления/добавления
        update_data = {}
        
        # Обязательные поля для новой записи
        if not user_row:
            update_data = {
                'Дата': current_date,
                'ТГ': f"@{username}",
                'Имя (тг)': first_name or "",
                'Статус': status or "Начал чат-бота",
                'День': current_day,
                'Месяц': current_month,
                'Год': current_year
            }
        
        # Обновляемые поля
        if first_name is not None:
            update_data['Имя (тг)'] = first_name
        if status is not None:
            update_data['Статус'] = status
        if gpt_response is not None:
            update_data['AI комент'] = gpt_response
        if full_name is not None:
            update_data['ФИО'] = full_name
        if phone_number is not None:
            update_data['Номер'] = phone_number
        if resume_link is not None:
            update_data['Ссылка на резюме'] = resume_link
        if interview_date is not None:
            update_data['Дата собеседования'] = interview_date
        if interview_time is not None:
            update_data['Время собесдеования'] = interview_time
        if qa_data is not None:
            update_data['Вопросы и ответы'] = qa_data
        
        # При статусе "Отказ" гарантируем сохранение ключевых данных
        if status == "Отказ":
            update_data.update({
                'ТГ': f"@{username}",
                'Дата': current_date,
                'Статус': "Отказ"
            })
        
        # Если пользователь существует - обновляем строку, иначе добавляем новую
        if user_row:
            # Получаем текущие значения
            current_values = data[user_row-2]
            
            # Обновляем только те поля, которые нужно изменить
            for key in update_data:
                current_values[key] = update_data[key]
            
            # Формируем полную строку для обновления (все 15 столбцов A-O)
            row_values = [
                current_values.get('Дата', ''),                   # A
                current_values.get('ТГ', ''),                     # B
                current_values.get('Имя (тг)', ''),               # C
                current_values.get('Статус', ''),                 # D
                '',                                               # E (пустой)
                current_values.get('ФИО', ''),                    # F
                current_values.get('Номер', ''),                  # G
                current_values.get('Ссылка на резюме', ''),       # H
                current_values.get('Дата собеседования', ''),     # I
                current_values.get('Время собесдеования', ''),    # J
                current_values.get('AI комент', ''),              # K
                current_values.get('Вопросы и ответы', ''),       # L
                current_values.get('День', ''),                   # M
                current_values.get('Месяц', ''),                  # N
                current_values.get('Год', '')                     # O
            ]
            
            await asyncio.to_thread(sheet.update, f'A{user_row}:O{user_row}', [row_values])
        else:
            # Формируем новую строку (все 15 столбцов A-O)
            new_row = [
                current_date,                   # A Дата
                f"@{username}",                # B ТГ
                first_name or "",              # C Имя (тг)
                status or "Начал чат-бота",    # D Статус
                "",                            # E (пустой)
                full_name or "",               # F ФИО
                phone_number or "",            # G Номер
                resume_link or "",             # H Ссылка на резюме
                interview_date or "",         # I Дата собеседования
                interview_time or "",         # J Время собеседования
                gpt_response or "",           # K AI комент
                qa_data or "",                # L Вопросы и ответы
                current_day,                  # M День
                current_month,                # N Месяц
                current_year                  # O Год
            ]
            await asyncio.to_thread(sheet.append_row, new_row)
        
        return True
    except Exception as e:
        print(f"Ошибка записи в Google Sheets: {e}")
        return False





async def check_empty_cells(sheet_id: str) -> InlineKeyboardMarkup | None:
    """
    Проверяет наличие пустых ячеек в столбцах дат (B2:AF2 - даты, B4:AF21 - данные)
    и создает кнопки для столбцов с пустыми ячейками
    """
    try:
        # Получаем объект таблицы (теперь await, так как функция асинхронная)
        sheet = await get_google_sheet(sheet_id, 0)
        
        # 1. Получаем заголовки (даты из строки 3)
        dates = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: sheet.row_values(3)[1:31]  # B3:AF3
        )
        
        # 2. Получаем данные (B4:AF21)
        data = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: sheet.get('B4:AF21')
        )
        
        keyboard = []
        max_buttons = 10
        buttons_added = 0
        now = datetime.now()
        current_date = now.date()


        # Проверяем каждый столбец (B-AF)
        for col_idx in range(len(dates)):
            if buttons_added >= max_buttons:
                break

            if col_idx < 26:  # B-Z (0-25)
                col_letter = chr(66 + col_idx)  # B=66, ..., Z=90
            else:  # AA-AF (26-30)
                col_letter = 'A' + chr(65 + (col_idx - 26))  # AA=65+0, AB=65+1, ..., AF=65+5
            has_empty = False
            
            # Проверяем ячейки в столбце (18 строк)
            for row_idx in range(min(len(data), 18)):
                if len(data[row_idx]) <= col_idx or data[row_idx][col_idx] == '':
                    has_empty = True
                    break
            
            try:
                date_str = dates[col_idx].split()[1]  # Получаем "31.03.2025"
                table_date = datetime.strptime(date_str, "%d.%m.%Y").date()
                is_future_date = table_date >= current_date  # True если дата >= сегодня
            except (ValueError, IndexError, AttributeError):
                is_future_date = False

            if has_empty and is_future_date:                
                date = dates[col_idx] if col_idx < len(dates) else f"Столбец {col_letter}"
                keyboard.append([
                    InlineKeyboardButton(
                        text=date,
                        callback_data=f"select_date_{col_letter}2"
                    )
                ])
                buttons_added += 1
        return InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None
        
    except Exception as e:
        logging.error(f"Ошибка в check_empty_cells: {str(e)}", exc_info=True)
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
        
        # Получаем объект листа (await, так как функция асинхронная)
        sheet = await get_google_sheet(sheet_id, 0)
        
        # Читаем данные асинхронно
        loop = asyncio.get_event_loop()
        time_values = await loop.run_in_executor(
            None, 
            lambda: sheet.get(time_range)
        )
        date_values = await loop.run_in_executor(
            None, 
            lambda: sheet.get(date_range)
        )
        
        # Создаем клавиатуру с доступным временем
        keyboard = []
        
        for i in range(len(time_values)):
            time_value = time_values[i][0] if i < len(time_values) and len(time_values[i]) > 0 else None
            date_value = date_values[i][0] if i < len(date_values) and len(date_values[i]) > 0 else None
            
            # Если есть время и нет записи в дате
            if time_value and not date_value:
                keyboard.append([
                    InlineKeyboardButton(
                        text=time_value,
                        callback_data=f"select_time_{column_letter}_{i+4}"  # i+4 соответствует реальной строке
                    )
                ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None
        
    except Exception as e:
        logging.error(f"Ошибка при проверке доступного времени: {e}")
        return None


async def clear_cell(sheet_id: str, cell_range: str) -> bool:
    """
    Очищает значение в указанной ячейке
    
    :param sheet_id: ID таблицы
    :param cell_range: Диапазон в формате 'A1' или 'Лист1!A1'
    :return: True если успешно, False при ошибке
    """
    try:
        sheet = await get_google_sheet(sheet_id, 0)  # 0 - индекс листа
        await asyncio.to_thread(sheet.update, cell_range, [['']])  # Записываем пустую строку
        return True
    except Exception as e:
        print(f"Ошибка очистки ячейки: {e}")
        return False

def parse_interview_datetime(date_str: str, time_str: str) -> datetime:
    
    date_part = date_str.split()[1]  
    date_obj = datetime.strptime(f"{date_part} {time_str}", "%d.%m.%Y %H:%M")
    return date_obj.replace(tzinfo=MOSCOW_TZ)  

async def get_job_data(sheet_id, state: FSMContext,):
    range_name = "A2:AG2"
    value = await get_google_sheet_data(sheet_id, range_name)
    row_data = value[0]
    await state.update_data(
        pd1=row_data[7],
        pd2=row_data[8],
        pd3=row_data[9],
        pd4=row_data[10],
        pd5=row_data[11],
        q1=row_data[12],
        q2=row_data[13],
        q3=row_data[14],
        q4=row_data[15],
        q5=row_data[16],
        q6=row_data[17],
        q7=row_data[18],
        q8=row_data[19],
        q9=row_data[20],
        q10=row_data[21],
        portrait=row_data[27],
        job_text=row_data[28],
        job_name=row_data[5],
        score = row_data[6],
        chat_id=row_data[1],
        text_1=row_data[30],
        text_2=row_data[31],
        text_3=row_data[32],
        video_1=row_data[22],
        video_2=row_data[23],
        video_3=row_data[24],
        video_4=row_data[25],
        video_5=row_data[26]
        )
    