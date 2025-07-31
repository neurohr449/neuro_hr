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
import aiofiles
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
    
async def handle_transcript(bot: Bot, file_id: str, is_video: bool = False) -> str:
    """Обработка медиафайла и возврат транскрипции"""
    try:
        
        temp_dir = "temp_audio"
        os.makedirs(temp_dir, exist_ok=True)
        file = await bot.get_file(file_id)
        input_path = os.path.join(temp_dir, f"input_{file_id}")
        await bot.download(file, destination=input_path)
        output_path = os.path.join(temp_dir, f"output_{file_id}.wav")
        if not is_video:
            os.system(
                f"ffmpeg -i {input_path} "
                f"-acodec pcm_s16le -ar 16000 -ac 1 -y {output_path}"
            )
        else:
            os.system(
                f"ffmpeg -i {input_path} -vn "
                f"-acodec pcm_s16le -ar 16000 -ac 1 -y {output_path}"
            )

        if not os.path.exists(output_path):
            return "Ошибка конвертации аудио"

        if os.path.getsize(output_path) > 24 * 1024 * 1024:
            return "Файл слишком большой (максимум 24MB)"
        
       
        with open(output_path, "rb") as audio_file:
            transcript = await client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
                language="ru"  
            )
        
        return transcript.text
    
    except Exception as e:
        print(f"Transcription error: {e}")
        return "Не удалось выполнить транскрибацию"
    
    finally:
        for path in [input_path, output_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass




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
    company_name: str = None,
    job_name: str = None,
    phone_number: str = None,
    resume_link: str = None,
    interview_date: str = None,
    interview_time: str = None,
    user_score: str = None,
    qa_data: str = None,
    chat_id: str = None
) -> bool:
    """
    Записывает или обновляет данные в Google Sheets с сохранением информации при отказе
    
    :param sheet_id: ID таблицы
    :param username: @username пользователя (обязательный параметр)
    :param first_name: Имя пользователя в Telegram
    :param status: Один из вариантов: '1.Начал чат-бота', '2.Собеседование', '3.Отказ'
    :param gpt_response: Комментарий AI (столбец O)
    :param full_name: ФИО (столбец I)
    :param company_name: Название компании (столбец G)
    :param job_name: Название вакансии (столбец H)
    :param phone_number: Номер телефона (столбец J)
    :param resume_link: Ссылка на резюме (столбец K)
    :param interview_date: Дата собеседования (столбец L)
    :param interview_time: Время собеседования (столбец M)
    :param user_score: Баллы (столбец N)
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
                'Имя (ТГ)': first_name or "",
                'Ссылка на переписку': f"https://t.me/{username}" or "",
                'Статус': status or "1.Начал чат-бота",
                'Название компании': company_name or "",
                'Название вакансии': job_name or "",
                'День': current_day,
                'Месяц': current_month,
                'Год': current_year
            }
        
        # Обновляемые поля
        if first_name is not None:
            update_data['Имя (ТГ)'] = first_name
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
        if user_score is not None:
            update_data['Баллы'] = user_score
        if company_name is not None:
            update_data['Название компании'] = company_name
        if job_name is not None:
            update_data['Название вакансии'] = job_name
        
        
        
        
        # При статусе "3.Отказ" гарантируем сохранение ключевых данных
        if status == "3.Отказ":
            update_data.update({
                'ТГ': f"@{username}",
                'Дата': current_date,
                'Статус': "3.Отказ"
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
                current_values.get('Имя (ТГ)', ''),               # C
                current_values.get('Ссылка на переписку', ''),    # D
                current_values.get('Статус', ''),                 # E
                '',                                               
                current_values.get('Название компании', ''),      # G
                current_values.get('Название вакансии', ''),      # H
                current_values.get('ФИО', ''),                    # I
                current_values.get('Номер', ''),                  # J
                current_values.get('Ссылка на резюме', ''),       # K
                current_values.get('Дата собеседования', ''),     # L
                current_values.get('Время собесдеования', ''),    # M
                current_values.get('Баллы', ''),                  # N
                current_values.get('AI комент', ''),              # O
                current_values.get('Вопросы и ответы', ''),       # P
                current_values.get('День', ''),                   # Q
                current_values.get('Месяц', ''),                  # R
                current_values.get('Год', '')                     # S
            ]
            
            await asyncio.to_thread(sheet.update, f'A{user_row}:S{user_row}', [row_values])
        else:
            # Формируем новую строку (все 15 столбцов A-O)
            new_row = [
                current_date,                  # A Дата
                f"@{username}",                # B ТГ
                first_name or "",              # C Имя (тг)
                f"https://t.me/{username}",    # D (пустой)
                status or "1.Начал чат-бота",  # E Статус
                "",                            # F (пустой)
                company_name or "",            # G Название компании
                job_name or "",                # H Название вакансии
                full_name or "",               # I ФИО
                phone_number or "",            # J Номер
                resume_link or "",             # K Ссылка на резюме
                interview_date or "",          # L Дата собеседования
                interview_time or "",          # M Время собеседования
                user_score or "",              # N Баллы
                gpt_response or "",            # O AI комент
                qa_data or "",                 # P Вопросы и ответы
                current_day,                   # Q День
                current_month,                 # R Месяц
                current_year,                  # S Год
                chat_id
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
            lambda: sheet.row_values(3)[1:71]  # B3:BS3
        )
        
        # 2. Получаем данные (B4:BS21)
        data = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: sheet.get('B4:BS21')
        )
        
        keyboard = []
        max_buttons = 10
        buttons_added = 0
        now = datetime.now()
        current_date = now.date()


        # Проверяем каждый столбец (B-BS)
        for col_idx in range(len(dates)):
            if buttons_added >= max_buttons:
                break

            # Преобразуем индекс в букву Excel-стиля (B, ..., Z, AA, ..., BS)
            if col_idx < 26:  # B-Z (0-25)
                col_letter = chr(66 + col_idx)  # B=66, ..., Z=90
            elif col_idx < 52:  # AA-AZ (26-51)
                col_letter = 'A' + chr(66 + (col_idx - 26))  # AA=65+0, ..., AZ=65+25
            else:  # BA-BS (52-69)
                col_letter = 'B' + chr(66 + (col_idx - 52))  # BA=65+0, ..., BS=65+17 (S=83)
            
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
        column_letter = re.sub(r"\d+", "", selected_date_cell)
        
        
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
        
        # Получаем дату из строки 3 (например "ПОНЕДЕЛЬНИК 14.04.2025")
        date_row = await loop.run_in_executor(
            None,
            lambda: sheet.get(f"{column_letter}3")
        )
        date_str = date_row[0][0] if date_row and len(date_row[0]) > 0 else ""
        
        # Парсим дату (формат "ПОНЕДЕЛЬНИК 14.04.2025")
        selected_date = None
        if date_str:
            try:
                date_part = date_str.split()[-1]  # берем часть после пробела (14.04.2025)
                selected_date = datetime.strptime(date_part, "%d.%m.%Y").date()
            except (ValueError, IndexError):
                pass
        
        # Получаем текущую дату и время
        now = datetime.now(MOSCOW_TZ)
        current_date = now.date()
        current_time = now.time()

        # Создаем клавиатуру с доступным временем
        keyboard = []
        
        for i in range(len(time_values)):
            time_value = time_values[i][0] if i < len(time_values) and len(time_values[i]) > 0 else None
            date_value = date_values[i][0] if i < len(date_values) and len(date_values[i]) > 0 else None
            
            # Если есть время и нет записи в дате
            if time_value and not date_value:
                # Проверяем, нужно ли учитывать текущее время (только для сегодняшней даты)
                if selected_date and selected_date == current_date:
                    try:
                        # Парсим время из таблицы (формат "13:30")
                        slot_time = datetime.strptime(time_value, "%H:%M").replace(tzinfo=MOSCOW_TZ).time()
                        # Пропускаем время, если оно уже прошло
                        if slot_time < current_time:
                            continue
                    except ValueError:
                        pass  # если не удалось распарсить время, оставляем кнопку
                
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




async def send_mail(state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    mail_sheet_id = user_data.get('mail_sheet_id')
    mail_text = user_data.get('mail_text')
    
    try:
        worksheet = await get_google_sheet(mail_sheet_id, 2)
        data = await asyncio.to_thread(worksheet.get_all_values)
        
        
        success_count = 0
        fail_count = 0
        fail_users  = []
        
        for row in data[1:]:  
            if len(row) > 19 and row[19].strip():  
                try:
                    chat_id = int(row[19].strip())  
                    await bot.send_message(
                        chat_id=chat_id,
                        text=mail_text
                    )
                    success_count += 1
                    await asyncio.sleep(0.3)  
                
                except ValueError:
                    fail_count += 1
                    fail_users.append(f"Некорректный chat_id: {row[19]}")
                    print(f"Некорректный chat_id: {row[19]}")
                
                except Exception as e:
                    fail_count += 1
                    fail_users.append(f"chat_id {row[19]}: {str(e)}")
                    print(f"Ошибка при отправке на chat_id {row[19]}: {e}")
        
        
        report = (
            f"Рассылка завершена!\n\n"
            f"Успешно отправлено: {success_count}\n"
            f"Не удалось отправить: {fail_count}\n"
        )
        
        if fail_users:
            report += f"\nОшибки отправки:\n" + "\n".join(fail_users[:10])  
            if len(fail_users) > 10:
                report += f"\n...и ещё {len(fail_users) - 10} ошибок"
        
        
        await bot.send_message(
            chat_id=state.key.chat_id,
            text=report
        )
        
    except Exception as e:
        error_msg = f"Произошла ошибка при выполнении рассылки: {e}"
        print(error_msg)
        await bot.send_message(
            chat_id=state.key.chat_id,
            text=error_msg
        )
    finally:
        await state.clear()





async def get_job_data(sheet_id, sheet_range, state: FSMContext,):
    range_name = f"A{sheet_range}:AO{sheet_range}"
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
        company_name=row_data[4],
        job_name=row_data[5],
        score = row_data[6],
        chat_id=row_data[1],
        text_1=row_data[30],
        text_2=row_data[31],
        text_3=row_data[32],
        text_4=row_data[33],
        text_5=row_data[34],
        text_6=row_data[35],
        text_7=row_data[36],
        text_8=row_data[37],
        
        decline_text = row_data[33],
        learn_text = row_data[38],
        practice_text = row_data[39],
        accept_text = row_data[40],
        
        video_1=row_data[22],
        video_2=row_data[23],
        video_3=row_data[24],
        video_4=row_data[25],
        video_5=row_data[26]
        )
    