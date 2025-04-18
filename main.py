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
from functions import *

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
            user = callback_query.from_user
            username = user.username
            first_name = user.first_name
            user_check = await write_to_google_sheet(
                                sheet_id = sheet_id, 
                                username = username,
                                first_name = first_name
                         )
            if user_check != False:
                await get_job_data(sheet_id, state)
                user_data = await state.get_data()
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Продолжить", callback_data="next")]
                ])
                await callback_query.message.answer(f"{user_data.get('pd1')}", reply_markup = keyboard)
                await state.set_state(UserState.pd1)
                await callback_query.answer()
            else:
                 await callback_query.message.answer("Вы уже получили отказ или произошла ошибка", reply_markup = FAIL_KEYBOARD)
    except Exception as e:
            await callback_query.message.answer(f"❌ Ошибка при загрузке данных: {str(e)}", reply_markup = FAIL_KEYBOARD)

@router.callback_query(StateFilter(UserState.pd1))
async def pd2(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Продолжить", callback_data="next")]
    ])
    await callback_query.message.answer(f"{user_data.get('pd2')}", reply_markup = keyboard)
    await state.set_state(UserState.pd2)
    await callback_query.answer()

@router.callback_query(StateFilter(UserState.pd2))
async def pd3(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Продолжить", callback_data="next")]
    ])
    await callback_query.message.answer(f"{user_data.get('pd3')}", reply_markup = keyboard)
    await state.set_state(UserState.pd3)
    await callback_query.answer()

@router.callback_query(StateFilter(UserState.pd3))
async def pd4(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Продолжить", callback_data="next")]
    ])
    await callback_query.message.answer(f"{user_data.get('pd4')}", reply_markup = keyboard)
    await state.set_state(UserState.pd4)
    await callback_query.answer()

@router.callback_query(StateFilter(UserState.pd4))
async def pd5(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Продолжить", callback_data="next")]
    ])
    await callback_query.message.answer(f"{user_data.get('pd5')}", reply_markup = keyboard)
    await state.set_state(UserState.pd5)
    await callback_query.answer()






@router.callback_query(StateFilter(UserState.pd5))
async def q1(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = "Работа с высоким доходом и крутой командой? Всё просто!\n\n1️⃣Пройдите короткий тест — всего 5-10 минут.\n\n2️⃣Ответьте, пожалуйста на 10 вопросов, своими словами обычным текстом на 1-3 предложения, как понимаете вопрос — без сложных текстов.\n\n3️⃣В конце — запишите кружок в Telegram (30-60 секунд), просто чтобы познакомиться!\n\n4️⃣Запишитесь на собеседование в два клика через чат-бота.🔥Все быстро, просто и без стресса!"
    await callback_query.message.answer(f"{text}")
    await callback_query.answer()
    await callback_query.message.answer(f"{user_data.get('q1')}")
    await state.set_state(UserState.q1)


@router.message(StateFilter(UserState.q1))
async def q2(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans1=ans1)
    user_data = await state.get_data()
    await message.answer(f"{user_data.get('q2')}")
    await state.set_state(UserState.q2)


@router.message(StateFilter(UserState.q2))
async def q3(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans2=ans1)
    user_data = await state.get_data()
    await message.answer(f"{user_data.get('q3')}")
    await state.set_state(UserState.q3)

@router.message(StateFilter(UserState.q3))
async def q4(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans3=ans1)
    user_data = await state.get_data()
    await message.answer(f"{user_data.get('q4')}")
    await state.set_state(UserState.q4)

@router.message(StateFilter(UserState.q4))
async def q5(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans4=ans1)
    user_data = await state.get_data()
    await message.answer(f"{user_data.get('q5')}")
    await state.set_state(UserState.q5)

@router.message(StateFilter(UserState.q5))
async def q6(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans5=ans1)
    user_data = await state.get_data()
    await message.answer(f"{user_data.get('q6')}")
    await state.set_state(UserState.q6)

@router.message(StateFilter(UserState.q6))
async def q7(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans6=ans1)
    user_data = await state.get_data()
    await message.answer(f"{user_data.get('q7')}")
    await state.set_state(UserState.q7)

@router.message(StateFilter(UserState.q7))
async def q8(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans7=ans1)
    user_data = await state.get_data()
    await message.answer(f"{user_data.get('q8')}")
    await state.set_state(UserState.q8)

@router.message(StateFilter(UserState.q8))
async def q9(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans8=ans1)
    user_data = await state.get_data()
    await message.answer(f"{user_data.get('q9')}")
    await state.set_state(UserState.q9)

@router.message(StateFilter(UserState.q9))
async def q10(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans9=ans1)
    user_data = await state.get_data()
    await message.answer(f"{user_data.get('q10')}")
    await state.set_state(UserState.q10)




@router.message(StateFilter(UserState.q10))
async def process_answers(message: Message, state: FSMContext):
    ans10 = message.text
    await state.update_data(ans10=ans10)
    text = "Спасибо за прохождение тестирования! \n\n📝В данный момент идет его проверка, и это займет всего 1 минуту ⏳.\n\nПожалуйста, подождите немного, и мы сообщим вам результат.\n\n❗️На другие кнопки пока идет проверка нажимать не нужно.\n\nВаше терпение очень ценится! 🙏"
    await message.answer(f"{text}")
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    
    promt = f"Ты HR менеджер с опытом более 30 лет в найме, поиске и обучении персонала, с учетом всего своего опыта, чтобы в будущем подобрать идеального кандидата для нашей вакансии: {user_data.get('job_name')}, тебе надо принять решение, пригласить кандидата на собеседование или отказать. Не нужно давать комментарий, нужно только решение, одно слово \"Собеседование\" или \"Отказ\"(Обязательно без спецсимволов, например точки). Для принятия решения сравни текст вакансии {user_data.get('job_text')}, портрет кандидата {user_data.get('portrait')} и вопросы и ответы пользователя который надо оценить и написать. Вопрос 1: {user_data.get('q1')}, ответ: {user_data.get('ans1')}; Вопрос 2: {user_data.get('q2')}, ответ: {user_data.get('ans2')}; Вопрос 3: {user_data.get('q3')}, ответ: {user_data.get('ans3')}; Вопрос 4: {user_data.get('q4')}, ответ: {user_data.get('ans4')}; Вопрос 5: {user_data.get('q5')}, ответ: {user_data.get('ans5')}; Вопрос 6: {user_data.get('q6')}, ответ: {user_data.get('ans6')}; Вопрос 7:{user_data.get('q7')}, ответ: {user_data.get('ans7')}; Вопрос 8: {user_data.get('q8')}, ответ: {user_data.get('ans8')}; Вопрос 9: {user_data.get('q9')}, ответ: {user_data.get('ans9')}; Вопрос 10:{user_data.get('q10')}, ответ: {user_data.get('ans10')}. Желаемая строгость оценки по десятибальной шкале 0 из 10(где 0 это принять всех кандидатов, а 10 Принять только идеального кандидата). Но помни про формат ответа"
    promt_2 = f"Ты HR менеджер с опытом более 30 лет в найме, поиске и обучении персонала, с учетом всего своего опыта, чтобы в будущем подобрать идеального кандидата для нашей вакансии: {user_data.get('job_name')}, тебе надо оценить кандидата, сравнить его с вакансией и написать комментарии что ты считаешь по нему. Вот вопросы и ответы пользователя который надо оценить и написать свои комментарии по кандидату строго до 1000 символов: Вопрос 1: {user_data.get('q1')}, ответ: {user_data.get('ans1')}; Вопрос 2: {user_data.get('q2')}, ответ: {user_data.get('ans2')}; Вопрос 3: {user_data.get('q3')}, ответ: {user_data.get('ans3')}; Вопрос 4: {user_data.get('q4')}, ответ: {user_data.get('ans4')}; Вопрос 5: {user_data.get('q5')}, ответ: {user_data.get('ans5')}; Вопрос 6: {user_data.get('q6')}, ответ: {user_data.get('ans6')}; Вопрос 7:{user_data.get('q7')}, ответ: {user_data.get('ans7')}; Вопрос 8: {user_data.get('q8')}, ответ: {user_data.get('ans8')}; Вопрос 9: {user_data.get('q9')}, ответ: {user_data.get('ans9')}; Вопрос 10:{user_data.get('q10')}, ответ: {user_data.get('ans10')} Вот текст вакансии для анализа {user_data.get('job_text')} и портрет кандидата {user_data.get('portrait')}"
    user_qa = f"Вопрос 1: {user_data.get('q1')}, ответ: {user_data.get('ans1')}; Вопрос 2: {user_data.get('q2')}, ответ: {user_data.get('ans2')}; Вопрос 3: {user_data.get('q3')}, ответ: {user_data.get('ans3')}; Вопрос 4: {user_data.get('q4')}, ответ: {user_data.get('ans4')}; Вопрос 5: {user_data.get('q5')}, ответ: {user_data.get('ans5')}; Вопрос 6: {user_data.get('q6')}, ответ: {user_data.get('ans6')}; Вопрос 7:{user_data.get('q7')}, ответ: {user_data.get('ans7')}; Вопрос 8: {user_data.get('q8')}, ответ: {user_data.get('ans8')}; Вопрос 9: {user_data.get('q9')}, ответ: {user_data.get('ans9')}; Вопрос 10:{user_data.get('q10')}, ответ: {user_data.get('ans10')}"
    response = await get_chatgpt_response(promt)
    response_2 = await get_chatgpt_response(promt_2)
    await state.update_data(response=response, 
                            response_2=response_2,
                            user_qa = user_qa
                            )
    await message.answer(f"{response}\n\n {response_2}")
    if response == "Собеседование":
        await state.set_state(UserState.result_yes)
        await write_to_google_sheet(
             sheet_id = sheet_id, 
             username = message.from_user.username,
             first_name=message.from_user.first_name,
             status=response,
             gpt_response=response_2
             )
        if success:
            await message.answer("✅ Данные сохранены!")
        else:
            await message.answer("⚠️ Ошибка сохранения данных")
        await message.answer("Ты молодец! 🎉 Ты прошел тестирование, а теперь можешь записаться на собеседование. Просто следуй инструкциям чат-бота: ответь на пару вопросов и выбери удобную дату и время для собеседования. 🚀")
        await message.answer("Пожалуйста напишите ваше ФИО.")
    
    
    
    elif response == "Отказ":
          await state.set_state(UserState.result_no)
          await message.answer("К сожалению вы не проходите на следующий этап")
          # Записываем в таблицу
          success = await write_to_google_sheet(
          sheet_id=sheet_id,
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
        await state.set_state(UserState.slot_time)
    else:
        await callback.message.answer("К сожалению, на этот день нет свободных окон.")
    
    await callback.answer()



@router.callback_query(lambda c: c.data.startswith("select_time_"), UserState.slot_time)
async def process_time_selection(callback: CallbackQuery, state: FSMContext):
    try:
        # 1. Разбираем callback данные
        parts = callback.data.split("_")
        column_letter = parts[2].upper()  # Буква столбца (B, C, ...)
        row_number = parts[3]             # Номер строки
        
        # 2. Получаем данные из состояния
        user_data = await state.get_data()
        sheet_id = user_data.get('sheet_id')
        
        if not sheet_id:
            await callback.answer("❌ ID таблицы не найден", show_alert=True)
            return

        # 3. Получаем лист (асинхронно)
        sheet = await get_google_sheet(sheet_id, 0)
        
        target_cell = f"{column_letter}{row_number}"
        
        # 4. Проверяем ячейку (асинхронно через run_in_executor)
        cell_value = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: sheet.acell(target_cell).value
        )
        
        # 5. Проверка на занятость ячейки
        if cell_value and cell_value.strip() and cell_value.lower() != 'none':
            await callback.answer(
                f"⏳ Время занято: {cell_value}",
                show_alert=True
            )
            return

        # 6. Подготовка данных для записи
        record_text = (
            f"Дата Время #{user_data.get('response')}\n"
            f"Вакансия: {user_data.get('job_name')}"
            f"ФИО: {user_data.get('user_fio', 'Без имени')}"
            f"ТГ: @{callback.from_user.username}"
            f"Номер: {user_data.get('user_phone', 'Без телефона')}"
            f"Резюме: {user_data.get('user_resume')}"
            f"https://docs.google.com/spreadsheets/d/{user_data.get('sheet_id')}"
            f"AI комментарий:{user_data.get('response_2')}"
            
        )
        
        # 7. Запись в таблицу (асинхронно)
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: sheet.update(
                range_name=target_cell,
                values=[[record_text]],
                value_input_option='USER_ENTERED'
            )
        )
        
        # 8. Получаем время для отображения пользователю (асинхронно)
        time_value = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: sheet.acell(f'A{row_number}').value
        )
        
        # 9. Отправляем подтверждение пользователю
        await callback.message.edit_text(
            "✅ Запись успешна!\n"
            "Дата: Дата"
            f"⏰ Время: {time_value}\n"
            f"👤 Контакты: {record_text}"
        )
        chat_id = user_data.get('chat_id')
        await bot.send_message(chat_id, f"{record_text}")

        # 10. Сохраняем данные в Google Sheets (асинхронно)
        success = await write_to_google_sheet(
            sheet_id=sheet_id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
            status="Собеседование",
            gpt_response=user_data.get('gpt_response', ''),
            full_name=user_data.get('user_fio'),
            phone_number=user_data.get('user_phone'),
            resume_link=user_data.get('user_resume'),
            interview_date="Дата",
            interview_time="Время",
            qa_data=user_data.get('user_qa')
        )
        
        if not success:
            await callback.message.answer("⚠️ Ошибка сохранения данных в таблицу")
        
        await state.clear()
        
    except Exception as e:
        logging.error(f"Ошибка записи: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Ошибка сервера, попробуйте позже", show_alert=True)









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