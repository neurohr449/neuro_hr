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
    else:
        await message.answer("👋 Обычный запуск бота.")

    
    






key = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDe+KDvhHuqC1Sj\nddkLxDylvsMXa8GO3gOB4r6mIwer8u2hVSDGXzfTaf3FjFjT2yRjUIYcCBdGQUjA\ngEFP2on3hQ3mBv7RTJt/pnSUGhbiOq8tnOXN/qAxCAQgMxzMampUqshqV2wLon5C\nEBUtmF6N/+FJq6w7LTYEVvx0lAP2Y2hlKHSfK/2nCWaO2LQcQ6iM1gqHDhM6FP3G\ngC9N+1uxxSDZ5Gviyfer0nauESfHDIEjx2HoAABZHS89plNMDvmvY/uEZ5n3wU7M\ng9JkjU+2vXuH4HGmIBbb5b67LBbudyAUDI+41nymGdctORt5/X5LkEUYRTVHXKCC\n9YyUmAJVAgMBAAECggEARaGqjLI4dmWcdIHAmvqZH/+/aEiIBWhS+xSHClYlNq8i\nQ8BUgG7K/dR7Yl6OfPbSWcuTXhyuvAt2P1uuSdRLQsfEC+KCYHWGmCow/PFa1SKT\ng3CcmaSbfURuGWos46+V7kP5W7BadxWzTUk9e+Q6HylaP0oD+uUHGfraU0PIKwDR\n++/4VEzdPKQxxYPEPY49KwghUMHGiFdVI4f/M1lNpPUNoWcviWrvDRz8jaD7C/Uq\nTn0ELEGXQZxao6/nchrQgsqf1Chw8S2fveWoazPzoiyTNgec0uq3r5ImTawdYW6b\n/yL9OdNh7BOyRxvDcI/It8IxvGL90Y8v6mJzFziOzwKBgQD6md7Avu7nKOD+sOm6\n7Qbcc0TH8HYAk78kgmRJvCWmZ72TWiL+IBD9b7XLbANZxo8WNEAa5A2LdDfGHyCj\nXggaSxBFh46M2YFN7mSek5yUYsV+CHfYuw8ZGYA3NEkHKkXgfUPk6LxY/fAlrC4U\nnfTYLqwPrXs2z3fXEcmrVlsTuwKBgQDjxl9rfMIU0Q6dZLJki4YJV9YDerSs8zNA\nSrr634YBdgy/sfdKPf95bjnOCsEqG24V5xZrdGyX3VovOWuv6svlEb7xTFpnbRt/\nw3fTXE8QkfNh4zbNyLF1Tz9ssu30oqoFzD6IviUphhUptFn0BjcNDIaHOe9sIKLX\n/pj6IeR5LwKBgQCkzG96XZWKGo3rr7flH161tm/y9CUFuCOpBL6i5sHzrqEyt8Hv\nUHMb10y8G6oQbc1HEtFdXb+yh5juByZViM7XS6nFr6GE6rxn3W/6AKSlyFaLzVHT\nCyCgpu50X0PvHFObj4UIkizacRRuEc6z7DRJvleUb8dpggITQzVWIZH/ZQKBgAI7\nNUAWTshpa9062UyG2V9KDvylvRNcpongsYg3nFZzU5ilI6kEhnYoEETmchH5htCM\nHPocf9vU/UctJtLoV+r8i4RNnS0aMoTD426cnuGorFuvICBP8P0XM6Xa8t3MoiHA\naHRqeG65s4dfDuqHDQ8Bqme0t5W1lCLNia4ZmuVdAoGAWPVuERVh/CLA3L2JqxvB\nP5SP84RhXC0I5rW90r3LDAclgcuq2YYfRlKYup/ypsCy7uRLcH4OyEHR18bPav3V\ngd5zB+bHRggW7RXBXJFsSy4qgPdxF1pTCMaPKnAgEfvu+BiP2OR4DWXxZUMtdlQQ\nfVDW33bMm16F5xC/3s7/ZCg=\n-----END PRIVATE KEY-----\n"
  



















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