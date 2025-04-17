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
    
    # Асинхронное создание клиента
    client = await asyncio.get_event_loop().run_in_executor(
        None, 
        lambda: gspread.authorize(creds)
    )
    
    # Асинхронное открытие листа
    return await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: client.open_by_key(sheet_id).get_worksheet(list_index)
    )






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
    Записывает или обновляет данные в Google Sheets
    
    :param sheet_id: ID таблицы
    :param username: @username пользователя (обязательный параметр)
    :param first_name: Имя пользователя
    :param status: Один из вариантов: 'Начал чат-бота', 'Собеседование', 'Отказ'
    :param gpt_response: Ответ от GPT
    :param full_name: ФИО пользователя
    :param phone_number: Номер телефона
    :param resume_link: Ссылка на резюме
    :param interview_date: Дата собеседования
    :param interview_time: Время собеседования
    :param qa_data: Вопросы и ответы пользователя
    :return: True если запись успешна, False при ошибке
    """
    try:
        tz = ZoneInfo('Europe/Moscow')
        now = datetime.now(tz)
        current_date = now.strftime("%Y-%m-%d %H:%M:%S")
        current_day = now.strftime("%d")
        current_month = now.strftime("%m")
        current_year = now.strftime("%Y")
        
        # Получаем данные из таблицы
        loop = asyncio.get_event_loop()
        sheet = await loop.run_in_executor(None, get_google_sheet, sheet_id, 2)
        data = await loop.run_in_executor(None, sheet.get_all_records)
        
        # Проверяем, есть ли пользователь уже в таблице
        user_row = None
        for i, row in enumerate(data, start=2):  # начинаем с 2, так как первая строка - заголовки
            if f"@{username}".lower() == row.get('Ник Телеграм', '').lower():
                user_row = i
                break
        
        # Если пользователь найден и его статус "Отказ" - возвращаем False
        if user_row and status != "Отказ":
            existing_status = data[user_row-2].get('Статус', '')
            if existing_status == "Отказ":
                return False
        
        # Подготовка данных для обновления/добавления
        update_data = {}
        
        # Обязательные поля для новой записи
        if not user_row:
            update_data = {
                'Дата текущая': current_date,
                'Ник Телеграм': f"@{username}",
                'Имя в телеграм': first_name or "",
                'Статус': status or "Начал чат-бота",
                'Текущий день': current_day,
                'Текущий Месяц': current_month,
                'Текущий Год': current_year
            }
        
        # Обновляемые поля для существующей записи
        if first_name is not None:
            update_data['Имя в телеграм'] = first_name
        if status is not None:
            update_data['Статус'] = status
        if gpt_response is not None:
            update_data['Комментарий нейросети'] = gpt_response
        if full_name is not None:
            update_data['ФИО'] = full_name
        if phone_number is not None:
            update_data['Номер телефона'] = phone_number
        if resume_link is not None:
            update_data['Ссылка на резюме'] = resume_link
        if interview_date is not None:
            update_data['Дата собеседования'] = interview_date
        if interview_time is not None:
            update_data['Время собеседования'] = interview_time
        if qa_data is not None:
            update_data['Вопросы и ответы пользователя'] = qa_data
        
        # Если пользователь существует - обновляем строку, иначе добавляем новую
        if user_row:
            # Получаем текущие значения, чтобы не перезаписать пустыми значениями
            current_values = data[user_row-2]
            for key in update_data:
                if update_data[key] or key in ['Статус', 'Имя в телеграм']:  # Разрешаем пустые значения только для определенных полей
                    current_values[key] = update_data[key]
            
            # Формируем список значений для обновления
            row_values = [
                current_values.get('Дата текущая', ''),
                current_values.get('Ник Телеграм', ''),
                current_values.get('Имя в телеграм', ''),
                current_values.get('Статус', ''),
                '',  # Столбец E (пустой)
                current_values.get('ФИО', ''),
                current_values.get('Номер телефона', ''),
                current_values.get('Ссылка на резюме', ''),
                current_values.get('Дата собеседования', ''),
                current_values.get('Время собеседования', ''),
                current_values.get('Комментарий нейросети', ''),
                current_values.get('Вопросы и ответы пользователя', ''),
                current_values.get('Текущий день', ''),
                current_values.get('Текущий Месяц', ''),
                current_values.get('Текущий Год', '')
            ]
            
            await loop.run_in_executor(None, sheet.update, f'A{user_row}:O{user_row}', [row_values])
        else:
            # Формируем новую строку
            new_row = [
                current_date,
                f"@{username}",
                first_name or "",
                status or "Начал чат-бота",
                "",  # Столбец E (пустой)
                full_name or "",
                phone_number or "",
                resume_link or "",
                interview_date or "",
                interview_time or "",
                gpt_response or "",
                qa_data or "",
                current_day,
                current_month,
                current_year
            ]
            await loop.run_in_executor(None, sheet.append_row, new_row)
        
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
        # Получаем объект таблицы (теперь await, так как функция асинхронная)
        sheet = await get_google_sheet(sheet_id, 0)
        
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
        
        keyboard = []
        
        # Проверяем каждый столбец (B-K)
        for col_idx in range(len(dates)):
            col_letter = chr(66 + col_idx)  # B=66, C=67,... K=75
            has_empty = False
            
            # Проверяем ячейки в столбце (18 строк)
            for row_idx in range(min(len(data), 18)):
                if len(data[row_idx]) <= col_idx or data[row_idx][col_idx] == '':
                    has_empty = True
                    break
            
            if has_empty:
                date = dates[col_idx] if col_idx < len(dates) else f"Столбец {col_letter}"
                keyboard.append([
                    InlineKeyboardButton(
                        text=date,
                        callback_data=f"select_date_{col_letter}2"
                    )
                ])
        
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



async def get_job_data(sheet_id, state: FSMContext,):
    range_name = "A2:AD2"
    value = await get_google_sheet_data(sheet_id, range_name)
    row_data = value[0]
    await state.update_data(
        pd1=row_data[6],
        pd2=row_data[7],
        pd3=row_data[8],
        pd4=row_data[9],
        pd5=row_data[10],
        q1=row_data[11],
        q2=row_data[12],
        q3=row_data[13],
        q4=row_data[14],
        q5=row_data[15],
        q6=row_data[16],
        q7=row_data[17],
        q8=row_data[18],
        q9=row_data[19],
        q10=row_data[20],
        portrait=row_data[26],
        job_text=row_data[27],
        job_name=row_data[5]
        )
    