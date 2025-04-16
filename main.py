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

BOT_TOKEN = os.getenv("BOT_TOKEN")
FAIL_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Попробовать снова", callback_data="retry")]
            ])
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
            text = "👋 Добро пожаловать в наш чат-бот! Мы рады, что вы здесь. \n\n🌟В этом боте вы сможете подробнее узнать про нашу компанию, вакансию, записаться на собеседование, пройти обучение и устроиться на работу 🍀💬⚠️ \n\nЕсли бот где-то не отвечает, подождите до 30 секунд, попробуйте повторно нажать на нужную кнопку или написать ее текстом, через 60 секунд выйти из бота и зайти обратно, а так же можете нажать на эту команду /start для запуска бота с начала."
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Поехали", callback_data="next")]
            ])
            
            await message.answer(f"{text}", reply_markup = keyboard)
        except Exception as e:
            await message.answer(f"❌ Ошибка при загрузке данных: {str(e)}", reply_markup = FAIL_KEYBOARD)
    else:
        await message.answer("👋 Добрый день. Запустите бота по уникальной ссылке!\n\nСсылка для тестов: https://t.me/pnhr_test_bot?start=1dM69zoKynsuN38Z7p2XtS09TXufwmo3cZL6bHi_zcyw")

    
@router.callback_query(StateFilter(UserState.welcome))
async def pd1(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    
    try:
            range_name = "F2:F2"
            data = await get_google_sheet_data(sheet_id,range_name)
            value = data[0][0]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
            await callback_query.message.answer(f"{value}", reply_markup = keyboard)
            await state.set_state(UserState.pd1)
    except Exception as e:
            await callback_query.message.answer(f"❌ Ошибка при загрузке данных: {str(e)}", reply_markup = FAIL_KEYBOARD)

@router.callback_query(StateFilter(UserState.pd1))
async def pd2(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    
    try:
            range_name = "G2:G2"
            data = await get_google_sheet_data(sheet_id,range_name)
            value = data[0][0]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
            await callback_query.message.answer(f"{value}", reply_markup = keyboard)
            await state.set_state(UserState.pd2)
    except Exception as e:
            await callback_query.message.answer(f"❌ Ошибка при загрузке данных: {str(e)}", reply_markup = FAIL_KEYBOARD)

@router.callback_query(StateFilter(UserState.pd2))
async def pd3(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    
    try:
            range_name = "H2:H2"
            data = await get_google_sheet_data(sheet_id,range_name)
            value = data[0][0]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
            await callback_query.message.answer(f"{value}", reply_markup = keyboard)
            await state.set_state(UserState.pd3)
    except Exception as e:
            await callback_query.message.answer(f"❌ Ошибка при загрузке данных: {str(e)}", reply_markup = FAIL_KEYBOARD)

@router.callback_query(StateFilter(UserState.pd3))
async def pd4(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    
    try:
            range_name = "I2:I2"
            data = await get_google_sheet_data(sheet_id,range_name)
            value = data[0][0]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
            await callback_query.message.answer(f"{value}", reply_markup = keyboard)
            await state.set_state(UserState.pd4)
    except Exception as e:
            await callback_query.message.answer(f"❌ Ошибка при загрузке данных: {str(e)}", reply_markup = FAIL_KEYBOARD)

@router.callback_query(StateFilter(UserState.pd4))
async def pd5(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    
    try:
            range_name = "J2:J2"
            data = await get_google_sheet_data(sheet_id,range_name)
            value = data[0][0]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
            await callback_query.message.answer(f"{value}", reply_markup = keyboard)
            await state.set_state(UserState.pd5)
    except Exception as e:
            await callback_query.message.answer(f"❌ Ошибка при загрузке данных: {str(e)}", reply_markup = FAIL_KEYBOARD)

@router.callback_query(StateFilter(UserState.pd5))
async def q1(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    text = "Работа с высоким доходом и крутой командой? Всё просто!\n\n1️⃣Пройдите короткий тест — всего 5-10 минут.\n\n2️⃣Ответьте, пожалуйста на 10 вопросов, своими словами обычным текстом на 1-3 предложения, как понимаете вопрос — без сложных текстов.\n\n3️⃣В конце — запишите кружок в Telegram (30-60 секунд), просто чтобы познакомиться!\n\n4️⃣Запишитесь на собеседование в два клика через чат-бота.🔥Все быстро, просто и без стресса!"
    await callback_query.message.answer(f"{text}")
    try:
            range_name = "K2:K2"
            data = await get_google_sheet_data(sheet_id,range_name)
            value = data[0][0]
            await state.update_data(question_1=value)
            await callback_query.message.answer(f"{value}")
            await state.set_state(UserState.q1)
    except Exception as e:
            await callback_query.message.answer(f"❌ Ошибка при загрузке данных: {str(e)}")

@router.message(StateFilter(UserState.q1))
async def q2(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans1=ans1)
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    
    try:
            range_name = "L2:L2"
            data = await get_google_sheet_data(sheet_id,range_name)
            value = data[0][0]
            await state.update_data(question_2=value)
            await message.answer(f"{value}")
            await state.set_state(UserState.q2)
    except Exception as e:
            await message.answer(f"❌ Ошибка при загрузке данных: {str(e)}")

@router.message(StateFilter(UserState.q2))
async def q3(message: Message, state: FSMContext):
    ans2 = message.text
    await state.update_data(ans2=ans2)
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    
    try:
            range_name = "M2:M2"
            data = await get_google_sheet_data(sheet_id,range_name)
            value = data[0][0]
            await state.update_data(question_3=value)
            await message.answer(f"{value}")
            await state.set_state(UserState.q3)
    except Exception as e:
            await message.answer(f"❌ Ошибка при загрузке данных: {str(e)}")

@router.message(StateFilter(UserState.q3))
async def q4(message: Message, state: FSMContext):
    ans3 = message.text
    await state.update_data(ans3=ans3)
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    
    try:
            range_name = "N2:N2"
            data = await get_google_sheet_data(sheet_id,range_name)
            value = data[0][0]
            await state.update_data(question_4=value)
            await message.answer(f"{value}")
            await state.set_state(UserState.q4)
    except Exception as e:
            await message.answer(f"❌ Ошибка при загрузке данных: {str(e)}")

@router.message(StateFilter(UserState.q4))
async def q5(message: Message, state: FSMContext):
    ans4 = message.text
    await state.update_data(ans4=ans4)
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    
    try:
            range_name = "O2:O2"
            data = await get_google_sheet_data(sheet_id,range_name)
            value = data[0][0]
            await state.update_data(question_5=value)
            await message.answer(f"{value}")
            await state.set_state(UserState.q5)
    except Exception as e:
            await message.answer(f"❌ Ошибка при загрузке данных: {str(e)}")

@router.message(StateFilter(UserState.q5))
async def q6(message: Message, state: FSMContext):
    ans5 = message.text
    await state.update_data(ans5=ans5)
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    
    try:
            range_name = "P2:P2"
            data = await get_google_sheet_data(sheet_id,range_name)
            value = data[0][0]
            await state.update_data(question_6=value)
            await message.answer(f"{value}")
            await state.set_state(UserState.q6)
    except Exception as e:
            await message.answer(f"❌ Ошибка при загрузке данных: {str(e)}")

@router.message(StateFilter(UserState.q6))
async def q7(message: Message, state: FSMContext):
    ans6 = message.text
    await state.update_data(ans6=ans6)
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    
    try:
            range_name = "Q2:Q2"
            data = await get_google_sheet_data(sheet_id,range_name)
            value = data[0][0]
            await state.update_data(question_7=value)
            await message.answer(f"{value}")
            await state.set_state(UserState.q7)
    except Exception as e:
            await message.answer(f"❌ Ошибка при загрузке данных: {str(e)}")

@router.message(StateFilter(UserState.q7))
async def q8(message: Message, state: FSMContext):
    ans7 = message.text
    await state.update_data(ans7=ans7)
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    
    try:
            range_name = "R2:R2"
            data = await get_google_sheet_data(sheet_id,range_name)
            value = data[0][0]
            await state.update_data(question_8=value)
            await message.answer(f"{value}")
            await state.set_state(UserState.q8)
    except Exception as e:
            await message.answer(f"❌ Ошибка при загрузке данных: {str(e)}")

@router.message(StateFilter(UserState.q8))
async def q9(message: Message, state: FSMContext):
    ans8 = message.text
    await state.update_data(ans8=ans8)
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    
    try:
            range_name = "S2:S2"
            data = await get_google_sheet_data(sheet_id,range_name)
            value = data[0][0]
            await state.update_data(question_9=value)
            await message.answer(f"{value}")
            await state.set_state(UserState.q9)
    except Exception as e:
            await message.answer(f"❌ Ошибка при загрузке данных: {str(e)}")

@router.message(StateFilter(UserState.q9))
async def q10(message: Message, state: FSMContext):
    ans9 = message.text
    await state.update_data(ans9=ans9)
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    
    try:
            range_name = "T2:T2"
            data = await get_google_sheet_data(sheet_id,range_name)
            value = data[0][0]
            await state.update_data(question_10=value)
            await message.answer(f"{value}")
            await state.set_state(UserState.q10)
    except Exception as e:
            await message.answer(f"❌ Ошибка при загрузке данных: {str(e)}")


@router.message(StateFilter(UserState.q10))
async def process_answers(message: Message, state: FSMContext):
    ans10 = message.text
    await state.update_data(ans10=ans10)
    text = "Спасибо за прохождение тестирования! \n\n📝В данный момент идет его проверка, и это займет всего 1 минуту ⏳.\n\nПожалуйста, подождите немного, и мы сообщим вам результат.\n\n❗️На другие кнопки пока идет проверка нажимать не нужно.\n\nВаше терпение очень ценится! 🙏"
    await message.answer(f"{text}")
    user_data = await state.get_data()



    sheet_id = user_data.get('sheet_id')
    
    try:
            range_name = "Z2:Z2"
            data = await get_google_sheet_data(sheet_id,range_name)
            value = data[0][0]
            await state.update_data(portrait=value)
    except Exception as e:
            await message.answer(f"❌ Ошибка при загрузке данных: {str(e)}")

    try:
            range_name = "AA2:AA2"
            data = await get_google_sheet_data(sheet_id,range_name)
            value = data[0][0]
            await state.update_data(job_text=value)
    except Exception as e:
            await message.answer(f"❌ Ошибка при загрузке данных: {str(e)}")
    try:
            range_name = "E2:E2"
            data = await get_google_sheet_data(sheet_id,range_name)
            value = data[0][0]
            await state.update_data(job_name=value)
    except Exception as e:
            await message.answer(f"❌ Ошибка при загрузке данных: {str(e)}")

    promt = f"Ты HR менеджер с опытом более 30 лет в найме, поиске и обучении персонала, с учетом всего своего опыта, чтобы в будущем подобрать идеального кандидата для нашей вакансии: {user_data.get('job_name')}, тебе надо принять решение, пригласить кандидата на собеседование или отказать. Не нужно давать комментарий, нужно только решение, одно слово \"Собеседование\" или \"Отказ\". Для принятия решения сравни текст вакансии {user_data.get('job_text')}, портрет кандидата {user_data.get('portrait')} и вопросы и ответы пользователя который надо оценить и написать. Вопрос 1: {user_data.get('question_1')}, ответ: {user_data.get('ans1')}; Вопрос 2: {user_data.get('question_2')}, ответ: {user_data.get('ans2')}; Вопрос 3: {user_data.get('question_3')}, ответ: {user_data.get('ans3')}; Вопрос 4: {user_data.get('question_4')}, ответ: {user_data.get('ans4')}; Вопрос 5: {user_data.get('question_5')}, ответ: {user_data.get('ans5')}; Вопрос 6: {user_data.get('question_6')}, ответ: {user_data.get('ans6')}; Вопрос 7:{user_data.get('question_7')}, ответ: {user_data.get('ans7')}; Вопрос 8: {user_data.get('question_8')}, ответ: {user_data.get('ans8')}; Вопрос 9: {user_data.get('question_9')}, ответ: {user_data.get('ans9')}; Вопрос 10:{user_data.get('question_10')}, ответ: {user_data.get('ans10')}"
    promt_2 = f"Ты HR менеджер с опытом более 30 лет в найме, поиске и обучении персонала, с учетом всего своего опыта, чтобы в будущем подобрать идеального кандидата для нашей вакансии: {user_data.get('job_name')}, тебе надо оценить кандидата, сравнить его с вакансией и написать комментарии что ты считаешь по нему. Вот вопросы и ответы пользователя который надо оценить и написать свои комментарии по кандидату строго до 1000 символов: Вопрос 1: {user_data.get('question_1')}, ответ: {user_data.get('ans1')}; Вопрос 2: {user_data.get('question_2')}, ответ: {user_data.get('ans2')}; Вопрос 3: {user_data.get('question_3')}, ответ: {user_data.get('ans3')}; Вопрос 4: {user_data.get('question_4')}, ответ: {user_data.get('ans4')}; Вопрос 5: {user_data.get('question_5')}, ответ: {user_data.get('ans5')}; Вопрос 6: {user_data.get('question_6')}, ответ: {user_data.get('ans6')}; Вопрос 7:{user_data.get('question_7')}, ответ: {user_data.get('ans7')}; Вопрос 8: {user_data.get('question_8')}, ответ: {user_data.get('ans8')}; Вопрос 9: {user_data.get('question_9')}, ответ: {user_data.get('ans9')}; Вопрос 10:{user_data.get('question_10')}, ответ: {user_data.get('ans10')} Вот текст вакансии для анализа {user_data.get('job_text')} и портрет кандидата {user_data.get('portrait')}"
    response = await get_chatgpt_response(promt)
    response_2 = await get_chatgpt_response(promt_2)
    
    await message.answer(f"{response}\n\n {response_2}")
    if response == "Собеседование":
        await state.set_state(UserState.result_yes)
        await message.answer("Ты молодец! 🎉 Ты прошел тестирование, а теперь можешь записаться на собеседование. Просто следуй инструкциям чат-бота: ответь на пару вопросов и выбери удобную дату и время для собеседования. 🚀")
        await message.answer("Пожалуйста напишите ваше ФИО.")
    elif response == "Отказ":
          await state.set_state(UserState.result_no)
          await message.answer("К сожалению вы не проходите на следующий этап")
          # Записываем в таблицу
          success = await write_to_google_sheet(
          sheet_id=user_data['sheet_id'],
          username=message.from_user.username,
          first_name=message.from_user.first_name,
          status=response,  
          gpt_response=response_2
          )
    
          if success:
            await message.answer("✅ Данные сохранены!")
          else:
            await message.answer("⚠️ Ошибка сохранения данных")
          
@router.message(StateFilter(UserState.result_yes))
async def process_name(message: Message, state: FSMContext):
        user_fio = message.text
        await state.update_data(user_fio=user_fio)
        await state.set_state(UserState.user_resume)
        await message.answer("Пришлите, пожалуйста, ссылку на ваше резюме.\n\nВзять на резюме ссылку можно по следующей ссылке:https://hh.ru/applicant/resumes")

@router.message(StateFilter(UserState.user_resume))
async def process_resume(message: Message, state: FSMContext):
        user_resume = message.text
        await state.update_data(user_resume=user_resume)
        await state.set_state(UserState.user_phone)
        await message.answer("Напишите ваш телефон для связи.")       

@router.message(StateFilter(UserState.user_phone))
async def process_resume(message: Message, state: FSMContext):
        user_phone = message.text
        await state.update_data(user_phone=user_phone)
        await state.set_state(UserState.slot_day)
         
        # Получаем sheet_id из состояния или базы данных
        user_data = await state.get_data()
        sheet_id = user_data.get('sheet_id')
        
        # Получаем клавиатуру с кнопками
        keyboard = await check_empty_cells(sheet_id)
        
        if keyboard:
                await message.answer(
                "Выберите дату для записи",
                reply_markup=keyboard
                )
                
        else:
                await message.answer("Все ячейки заполнены!")



@router.callback_query(lambda c: c.data.startswith("select_date_"), UserState.slot_day)
async def process_date_selection(callback: CallbackQuery, state: FSMContext):
    # Получаем выбранную ячейку даты (например "B2")
    selected_date_cell = callback.data.split("_")[2]  # "select_date_B2" → "B2"
    
    # Получаем sheet_id из состояния
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    
    # Получаем клавиатуру с доступным временем
    keyboard = await get_available_times(sheet_id, selected_date_cell)
    
    if keyboard:
        await callback.message.answer(
            "Доступное время для записи:",
            reply_markup=keyboard
        )
    else:
        await callback.message.answer("К сожалению, на этот день нет свободных окон.")
    
    await callback.answer()



@router.callback_query(lambda c: c.data.startswith("select_time_"), UserState.slot_time)
async def process_time_selection(callback: CallbackQuery, state: FSMContext):
    # Пример callback_data: "select_time_B_5" (столбец B, строка 5)
    parts = callback.data.split("_")
    column_letter = parts[2]
    row_number = parts[3]
    
    # Сохраняем выбранный слот в состоянии
    await state.update_data({
        'selected_column': column_letter,
        'selected_row': row_number
    })
    
    await callback.message.answer(
        f"Вы выбрали время в ячейке {column_letter}{row_number}\n"
        "Введите ваши данные для записи:"
    )
    await callback.answer()









        







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


def get_google_sheet(sheet_id):
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file({
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
    return client.open_by_key(sheet_id).get_worksheet(2) 

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
        sheet = await loop.run_in_executor(None, get_google_sheet, sheet_id)
        await loop.run_in_executor(None, sheet.append_row, row_data)
        
        return True
    except Exception as e:
        print(f"Ошибка записи в Google Sheets: {e}")
        return False

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def check_empty_cells(sheet_id: str) -> InlineKeyboardMarkup | None:
    """
    Проверяет наличие пустых ячеек в столбцах B-K (диапазон B2:K21)
    и создает кнопки для столбцов с пустыми ячейками
    
    :param sheet_id: ID Google-таблицы
    :return: InlineKeyboardMarkup или None, если нет пустых ячеек
    """
    try:
        # Получаем данные из таблицы
        sheet = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: get_google_sheet(sheet_id).range('B2:K21')
        )
        
        # Транспонируем данные (столбцы -> строки)
        columns = list(zip(*[row for row in sheet]))
        
        # Получаем заголовки из строки 2 (B2:K2)
        headers = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: get_google_sheet(sheet_id).row_values(2)[1:10]  # B2:K2
        )
        
        keyboard = []
        
        # Проверяем каждый столбец (B-K)
        for col_idx, (column, header) in enumerate(zip(columns, headers)):
            col_letter = chr(66 + col_idx)  # B=66, C=67,... K=75
            
            # Проверяем есть ли пустые ячейки в столбце
            if any(cell.value == '' for cell in column):
                # Добавляем кнопку с заголовком столбца
                keyboard.append([
                    InlineKeyboardButton(
                        text=header,
                        callback_data=f"fill_{col_letter}"
                    )
                ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None
        
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        return None


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
        sheet = get_google_sheet(sheet_id)
        
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