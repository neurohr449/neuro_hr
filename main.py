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
import shelve

adminlist = [464682207, 389054202, 42599312, 7726313921]
my_tok = os.getenv("my_tok")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# from auth import BOT_TOKEN
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(
    parse_mode=ParseMode.HTML))
storage = MemoryStorage()
router = Router()
dp = Dispatcher(storage=storage)

class UserState(StatesGroup):
    add = State()
    deacti = State()
    get = State()

class StateMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        state = data['state']
        current_state = await state.get_state()
        data['current_state'] = current_state
        return await handler(event, data)

def load_adminlist():
    with shelve.open("admin_db") as db:
        return db.get("admins", adminlist)

def save_adminlist(admins):
    with shelve.open("admin_db", writeback=True) as db:
        db["admins"] = admins


async def repost_to_admin_ch(input):
    adminlist = load_adminlist()
    for admin_id in adminlist:
        await print(admin_id)
        return
    
async def get_date_time_backwards(days: int) -> str:
    now = datetime.now()
    past_date = now - timedelta(days=days)
    return past_date.strftime("%Y-%m-%d %H:%M:%S")

# def format_transaction_data(transactions):
#     formatted_messages = []
#     for transaction in transactions:
#         email = transaction.get('email')
#         amount = transaction.get('amount')
#         date_time_str = transaction.get('dateTime')
#         active = transaction.get('isActive')
#         if active:
#             active_emote = '✅'
#         if not active:
#             active_emote = '❌'
        
#         date_time = datetime.fromisoformat(date_time_str).strftime('%d-%m-%y')

#         formatted_message = f"{email} ({amount}) {date_time} {active_emote}"
#         formatted_messages.append(formatted_message)

#     return "\n".join(formatted_messages)

def parse_response(response):
    try:
        transaction = response[0]

        extra_data = json.loads(transaction['extra'])

        amount = f"{transaction['amount']} {extra_data['Currency']}" if 'Currency' in extra_data else f"{transaction['amount']} RUB"
        tg = transaction['userTgId']
        mail = transaction['email']
        active = transaction.get('isActive')
        if active:
            active_emote = '✅'
        if not active:
            active_emote = '❌'
        try:
            date = datetime.strptime(transaction['dateTime'], "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            date = datetime.strptime(transaction['dateTime'], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        # promo = transaction['promo'] if transaction['promo'] is not None else "None"
        # promo = transaction.get('promo', "None")  \npromo: {promo} 

        return f"amount: {amount}\ntg: {tg}\nmail: {mail}\ndate: {date}\nisActive: {active_emote}"
    except (IndexError, KeyError, json.JSONDecodeError) as e:
        print(e)
        return "Юзер в дб не найден"

async def get_req(method, inputname, input):
    url = f'https://nutridb-production.up.railway.app{method}?{inputname}={input}'
    print(url)

    headers = {
        "MyTok": my_tok
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"HTTP error! status: {response.status}")

                response_data = await response.json()
                print('Retrieved Data:', response_data)
                return response_data
        except Exception as e:
            print('Error retrieving data:', e)
            raise

@router.message(Command("addadmin"))
async def addadmin_handler(message: Message) -> None:
    adminlist = load_adminlist()
    args = message.text.split(maxsplit=1)
    if message.from_user.id not in adminlist:
        await message.answer("You don't have permissions to add an admin.")
        return
    if len(args) < 2:
        await message.reply("Please provide a user ID after the command.")
        return
    try:
        new_admin_id = int(args[1])
        if new_admin_id in adminlist:
            await message.reply(f"User ID {new_admin_id} is already an admin.")
        else:
            adminlist.append(new_admin_id)
            save_adminlist(adminlist)
            await message.reply(f"User ID {new_admin_id} has been added to the admin list.")
    except ValueError:
        await message.reply("Invalid user ID. Please provide a numeric user ID.")

@router.message(Command(commands=['getadmins']))
async def getadmins_handler(message: Message) -> None:
    adminlist = load_adminlist()
    await message.reply(f"{adminlist}")

@router.message(Command("menu"))
async def menu_handler(message: Message) -> None:
    adminlist = load_adminlist()
    args = message.text.split(maxsplit=1)
    if message.from_user.id not in adminlist:
        await message.answer("You don't have permissions")
        return
    elif message.from_user.id in adminlist: 
        await message.answer(
            "Менюшка",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Получить список", callback_data="handler_getsubs")],
                [InlineKeyboardButton(text="Выдать подписку", callback_data="addsub")],
                [InlineKeyboardButton(text="Отключить юзера", callback_data="deactivate")],
                [InlineKeyboardButton(text="Получить инфу по юзеру", callback_data="get_info")],
            ])
        )

@router.callback_query(lambda c: c.data == 'handler_getsubs')
async def process_handler_getsubs(callback_query: CallbackQuery, state: FSMContext):
    adminlist = load_adminlist()
    if callback_query.from_user.id not in adminlist:
        await callback_query.message.answer("You don't have permissions")
        return
    elif callback_query.from_user.id in adminlist: 
        await callback_query.message.answer(
            "За какой срок хочешь юзеров?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="1", callback_data="getsubstime_1")],
                [InlineKeyboardButton(text="7", callback_data="getsubstime_7")],
                [InlineKeyboardButton(text="14", callback_data="getsubstime_14")],
                [InlineKeyboardButton(text="30", callback_data="getsubstime_30")],
            ])
        )
        await callback_query.answer()

@router.callback_query(lambda c: c.data.startswith('getsubstime_'))
async def process_time_period(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.from_user.id not in adminlist:
        await callback_query.message.answer("You don't have permissions")
        return
    elif callback_query.from_user.id in adminlist: 
        days = int(callback_query.data.split('_')[1])
        result_date = await get_date_time_backwards(days)
        await callback_query.message.answer(f"Here is the date {days} days ago: {result_date}")
        response = await get_req("/api/Subscription/GetSubs", "MyDateTime", result_date)
        # response_formatted = format_transaction_data(response)
        # await callback_query.message.answer(str(response_formatted))
        await handle_response(callback_query, response)


@router.callback_query(lambda c: c.data == 'addsub')
async def process_addsub(callback_query: CallbackQuery, state: FSMContext):
    adminlist = load_adminlist()
    if callback_query.from_user.id not in adminlist:
        await callback_query.message.answer("You don't have permissions")
        return
    elif callback_query.from_user.id in adminlist: 
        await state.set_state(UserState.add)
        await callback_query.message.answer("Пиши почту")
        await callback_query.answer()

@router.callback_query(lambda c: c.data == 'deactivate')
async def process_deactivate(callback_query: CallbackQuery, state: FSMContext):
    adminlist = load_adminlist()
    if callback_query.from_user.id not in adminlist:
        await callback_query.message.answer("You don't have permissions")
        return
    elif callback_query.from_user.id in adminlist: 
        await state.set_state(UserState.deacti)
        await callback_query.message.answer("Пиши Email")
        await callback_query.answer()

@router.callback_query(lambda c: c.data == 'get_info')
async def process_get_info(callback_query: CallbackQuery, state: FSMContext):
    adminlist = load_adminlist()
    if callback_query.from_user.id not in adminlist:
        await callback_query.message.answer("You don't have permissions")
        return
    elif callback_query.from_user.id in adminlist: 
        await state.set_state(UserState.get)
        await callback_query.message.answer("Пиши Email")
        await callback_query.answer()

@router.message(StateFilter(UserState.add))
async def process_add(message: Message, state: FSMContext):
    adminlist = load_adminlist()
    if message.from_user.id not in adminlist:
        await message.answer("You don't have permissions")
        return
    elif message.from_user.id in adminlist: 
        response = await get_req("/api/Subscription/AddSub", "Email", message.text)
        
        await message.answer(f"Статус выдачи подписки пользователю {message.text}: {str(response)}")
        await state.clear()
        return

@router.message(StateFilter(UserState.deacti))
async def process_deacti(message: Message, state: FSMContext):
    adminlist = load_adminlist()
    if message.from_user.id not in adminlist:
        await message.answer("You don't have permissions")

        await state.clear()
        return
    elif message.from_user.id in adminlist: 
        response = await get_req("/api/Subscription/DeactivateUser", "Email", message.text)

        await message.answer(f"Статус деактивации пользователя {message.text}: {str(response)}")
        await state.clear()
        return

@router.message(StateFilter(UserState.get))
async def process_get(message: Message, state: FSMContext):
    adminlist = load_adminlist()
    if message.from_user.id not in adminlist:
        await message.answer("You don't have permissions")
        await state.clear()
        return
    elif message.from_user.id in adminlist: 
        print('hit_get')
        response = await get_req("/api/Subscription/GetUserSub", "Email", message.text)
        answer = parse_response(response)
        
        await message.answer(answer)

        await state.clear()
        return

async def send_long_message(message, text, max_length=4096):
    lines = text.split('\n')
    chunk = ""
    
    for line in lines:
        if len(chunk) + len(line) + 1 > max_length:
            if chunk:
                await message.answer(chunk)
                chunk = ""
        chunk += line + '\n'
    
    if chunk:
        await message.answer(chunk)

async def handle_response(callback_query, response):
    response_formatted = format_transaction_data(response)
    await send_long_message(callback_query.message, response_formatted)

def format_transaction_data(transactions):
    formatted_messages = []
    for transaction in transactions:
        email = transaction.get('email')
        amount = transaction.get('amount')
        date_time_str = transaction.get('dateTime')
        active = transaction.get('isActive')
        active_emote = '✅' if active else '❌'
        
        date_time = datetime.fromisoformat(date_time_str).strftime('%d-%m-%y')

        formatted_message = f"{email} ({amount}) {date_time} {active_emote}"
        formatted_messages.append(formatted_message)

    return "\n".join(formatted_messages)

async def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    dp.include_router(router)
    dp.message.middleware(StateMiddleware())
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(
        parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())