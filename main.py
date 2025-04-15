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

BOT_TOKEN = os.getenv("BOT_TOKEN")

# from auth import BOT_TOKEN
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(
    parse_mode=ParseMode.HTML))
storage = MemoryStorage()
router = Router()
dp = Dispatcher(storage=storage)

class UserState(StatesGroup):
    welcome = State()
    pd1 = State()
    pd2 = State()
    pd3 = State()
    pd4 = State()
    pd5 = State()
    s_test = State()
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
    q6 = State()
    q7 = State()
    q8 = State()
    q9 = State()
    q10 = State()
    result_no = State()
    result_yes = State()
    user_name = State()
    user_phone = State()
    user_resume = State()
    slot_day = State()
    slot_time = State()

@router.message(CommandStart())
async def command_start_handler(message: Message, command: CommandObject, state: FSMContext) -> None:
    await state.set_state(UserState.welcome)
    sheet_id  = command.args
    if sheet_id:
        try:
            await state.update_data(sheet_id=sheet_id)
            range_name = "B1:AB1"
            data = await get_google_sheet_data(sheet_id,range_name)
            formatted_data = "\n".join([", ".join(row) for row in data])
            await message.answer(f"📊 Данные из таблицы:\n{formatted_data}")
        except Exception as e:
            await message.answer(f"❌ Ошибка при загрузке данных: {str(e)}")
            key = os.getenv("GS_PRIVATE_KEY")
            print(f"Длина ключа: {len(key)} символов")
            print(f"Начинается с: {key[:20]}...")
            print(f"Заканчивается на: ...{key[-20:]}")
            required_vars = [
                "GS_TYPE", "GS_PROJECT_ID", "GS_PRIVATE_KEY_ID",
                "GS_CLIENT_EMAIL", "GS_CLIENT_ID"
            ]
            for var in required_vars:
                print(f"{var}: {bool(os.getenv(var))}")
    else:
        await message.answer("👋 Обычный запуск бота.")

    
    

























async def get_google_sheet_data(sheet_id: str, range_name: str = "A1:C10"):
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
    sheet = client.open_by_key(sheet_id).sheet1 
    data = sheet.get(range_name)
    return data



##########################################################################################################################################################################################################
##########################################################################################################################################################################################################
##########################################################################################################################################################################################################
class StateMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        state = data['state']
        current_state = await state.get_state()
        data['current_state'] = current_state
        return await handler(event, data)

async def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    dp.include_router(router)
    dp.message.middleware(StateMiddleware())
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(
        parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())