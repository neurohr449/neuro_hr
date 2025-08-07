import asyncio
import logging
import sys
import os
import json
from datetime import datetime, timedelta
import aiohttp
from aiogram import Bot, Dispatcher, html, Router, BaseMiddleware
from aiogram import F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters.command import CommandObject
from aiogram.exceptions import TelegramBadRequest
import shelve
import gspread
import re


from google.oauth2.service_account import Credentials
from openai import AsyncOpenAI
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from functions import *
from database import *

BOT_TOKEN = os.getenv("BOT_TOKEN")
FAIL_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Попробовать снова", callback_data="retry")]
            ])
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MOSCOW_TZ = ZoneInfo("Europe/Moscow")
SERVER_TZ = ZoneInfo("UTC")
TELEGRAM_VIDEO_PATTERN = r'https://t\.me/'


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
    process_time_change = State()
    mail_1 = State()
    mail_2 = State()
    mail_3 = State()
    select_vacancy = State()



@router.message(CommandStart())
async def command_start_handler(message: Message, command: CommandObject, state: FSMContext) -> None:
    await state.set_state(UserState.welcome)
    args = command.args
    if args:
        parts = args.rsplit('_', 1)
        sheet_id  = parts[0]
        sheet_range = parts[1]    
        if len(parts) > 1 and parts[1].isdigit():  
            sheet_id = parts[0]  
            sheet_range = parts[1]  
        else:  
            sheet_id = args  
            sheet_range = 2
        
        print(f"sheetid {sheet_id}", "sheet_range",sheet_range)
    else:
        await message.answer("👋 Здравствуйте. Запустите бота по уникальной ссылке!")
        

    if sheet_id:
        try:
            await state.update_data(sheet_id=sheet_id,
                                    sheet_range=sheet_range)
            text = "👋 Добро пожаловать в наш чат-бот! Мы рады, что вы здесь. \n\n🌟В этом боте вы сможете подробнее узнать про нашу компанию, вакансию и записаться на собеседование 🍀💬⚠️ \n\nЕсли бот где-то не отвечает, подождите до 30 секунд, попробуйте повторно нажать на нужную кнопку или написать ее текстом, через 60 секунд выйти из бота и зайти обратно, а так же можете нажать на эту команду /start для запуска бота с начала."
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Поехали", callback_data="next")]
            ])
            
            await message.answer(f"{text}", reply_markup = keyboard)
        except Exception as e:
            await message.answer(f"❌ Ошибка при загрузке данных: {str(e)}", reply_markup = FAIL_KEYBOARD)
    else:
        await message.answer("👋 Здравствуйте. Запустите бота по уникальной ссылке!")


#\n\nСсылка для тестов: https://t.me/pnhr_test_bot?start=1dM69zoKynsuN38Z7p2XtS09TXufwmo3cZL6bHi_zcyw


@router.callback_query(lambda c: c.data == 'notification')
async def notification_cb_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == UserState.pd1.state:
         await pd1(callback_query, state)
    elif current_state == UserState.pd2.state:
         await pd2(callback_query, state)
    elif current_state == UserState.pd3.state:
         await pd3(callback_query, state)
    elif current_state == UserState.pd4.state:
         await pd4(callback_query, state)
    elif current_state == UserState.pd5.state:
         await pd5(callback_query, state)
    elif current_state == UserState.q1.state:
         await q1(callback_query, state)
    elif current_state == UserState.q2.state:
         await q2(callback_query.message, state)
    elif current_state == UserState.q3.state:
         await q3(callback_query.message, state)
    elif current_state == UserState.q4.state:
         await q4(callback_query.message, state)
    elif current_state == UserState.q5.state:
         await q5(callback_query.message, state)
    elif current_state == UserState.q6.state:
         await q6(callback_query.message, state)
    elif current_state == UserState.q7.state:
         await q7(callback_query.message, state)
    elif current_state == UserState.q8.state:
         await q8(callback_query.message, state)
    elif current_state == UserState.q9.state:
         await q9(callback_query.message, state)
    elif current_state == UserState.q10.state:
         await q10(callback_query.message, state)
    



@router.message(Command("get_chat_id"))
async def chat_command(message: Message, state: FSMContext):
    chat_id = message.chat.id
    chat_type = message.chat.type
    await message.reply(
        f"🆔 Chat ID: <code>{chat_id}</code>\n"
        f"📌 Тип чата: {chat_type}",
        parse_mode="HTML"
    )





@router.message(Command("mail"))
async def mail_command(message: Message, state: FSMContext):
    await state.set_state(UserState.mail_1)
    await message.answer("Пришлите ссылку на вашу Google таблицу")

@router.message(StateFilter(UserState.mail_1))
async def mail_sheet(message: Message, state: FSMContext):
    mail_sheet_id_raw = message.text
    parts = mail_sheet_id_raw.split('/')
    mail_sheet_id = parts[5] if mail_sheet_id_raw.startswith("http") else parts[3]
    
    if mail_sheet_id:
        vacancies = await get_vacancies(mail_sheet_id)
        
        if not vacancies:
            await message.answer("В таблице не найдено вакансий")
            return
        
        seen = set()
        unique_vacancies = []
        for vac in vacancies:
            if vac not in seen:
                seen.add(vac)
                unique_vacancies.append(vac)
        


        await state.update_data(
            mail_sheet_id=mail_sheet_id,
            mail_sheet=mail_sheet_id_raw,
            vacancies=unique_vacancies
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=vacancy, callback_data=f"vacancy_{i}")]
            for i, vacancy in enumerate(unique_vacancies)
        ])
        
        await state.set_state(UserState.select_vacancy)
        await message.answer("Выберите вакансию для рассылки:", reply_markup=keyboard)

@router.callback_query(StateFilter(UserState.select_vacancy))
async def select_vacancy(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith("vacancy_"):
        vacancy_index = int(callback.data.split('_')[1])
        user_data = await state.get_data()
        selected_vacancy = user_data['vacancies'][vacancy_index]
        
        await state.update_data(selected_vacancy=selected_vacancy)
        await state.set_state(UserState.mail_2)
        await callback.message.answer(
            f"Выбрана вакансия: {selected_vacancy}\n\n"
            "Пришлите текст рассылки"
        )

@router.message(StateFilter(UserState.mail_2))
async def mail_text(message: Message, state: FSMContext):
    mail_text = message.text
    await state.update_data(mail_text=mail_text)
    await state.set_state(UserState.mail_3)
    
    user_data = await state.get_data()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сделать рассылку", callback_data="mail_next")],
        [InlineKeyboardButton(text="Изменить", callback_data="edit")]
    ])
    
    text = (
        f"Рассылка будет сделана для вакансии: {user_data['selected_vacancy']}\n"
        f"Таблица: {user_data['mail_sheet']}\n\n"
        f"Текст рассылки:\n{mail_text}"
    )
    
    await message.answer(text=text, reply_markup=keyboard, disable_web_page_preview=True)


@router.callback_query(StateFilter(UserState.mail_3))
async def mail_start(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == "edit":
        await state.set_state(UserState.mail_1)
        await callback_query.message.answer("Пришлите ссылку на вашу Google таблицу")
    elif callback_query.data == "mail_next":
        await send_mail(state, bot)




@router.callback_query(StateFilter(UserState.welcome))
async def pd1(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    sheet_range= user_data.get('sheet_range')
    await state.update_data(
        survey_started=datetime.now(),
        survey_completed=False
    )
    asyncio.create_task(check_survey_completion(callback_query.message.chat.id, state))
    
    try:
            await get_job_data(sheet_id, sheet_range, state)
            user = callback_query.from_user
            username = user.username
            first_name = user.first_name
            company_name = user_data.get('company_name')
            job_name = user_data.get('job_name')
            chat_id = callback_query.message.chat.id
            user_check = await write_to_google_sheet(
                                sheet_id = sheet_id, 
                                username = username,
                                first_name = first_name,
                                company_name = company_name,
                                job_name = job_name,
                                chat_id=chat_id
                         )
            if user_check != False:
                
                user_data = await state.get_data()
                text = user_data.get('pd1')
                if text:
                    match = re.search(TELEGRAM_VIDEO_PATTERN, user_data.get('video_1'))
                    if match:
                        media_url = user_data.get('video_1')           
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="Продолжить", callback_data="next")]
                        ])
                        media_sent = False
                        if not media_sent:
                            try:
                                await callback_query.message.answer_video(video=media_url)
                                media_sent = True
                            except TelegramBadRequest:
                                pass

                        if not media_sent:
                            try:
                                await callback_query.message.answer_photo(photo=media_url)
                                media_sent = True
                            except TelegramBadRequest:
                                pass

                        if not media_sent:
                            try:
                                await callback_query.message.answer_audio(audio=media_url)
                                media_sent = True
                            except TelegramBadRequest:
                                pass

                        await callback_query.message.answer(text=f"{user_data.get('pd1')}", reply_markup = keyboard)
                        await state.set_state(UserState.pd1)
                        await callback_query.answer()
                    else:                    
                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="Продолжить", callback_data="next")]
                        ])
                        await callback_query.message.answer(f"{user_data.get('pd1')}", reply_markup = keyboard)
                        await state.set_state(UserState.pd1)
                        await callback_query.answer()
                else:
                    await state.set_state(UserState.pd5)
                    await q1(callback_query, state)     
            else:
                 await callback_query.message.answer("Вы уже получили отказ")
    except Exception as e:
            await callback_query.message.answer(f"❌ Ошибка при загрузке данных: {str(e)}", reply_markup = FAIL_KEYBOARD)



@router.callback_query(StateFilter(UserState.pd1))
async def pd2(callback_query: CallbackQuery, state: FSMContext):
    
    user_data = await state.get_data()
    text = user_data.get('pd2')
    if text:
        match = re.search(TELEGRAM_VIDEO_PATTERN, user_data.get('video_2'))
        if match:           
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
            await callback_query.message.answer_video(video=user_data.get('video_2'))
            await callback_query.message.answer(text=f"{user_data.get('pd2')}", reply_markup = keyboard)
            await state.set_state(UserState.pd2)
            await callback_query.answer()
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
            await callback_query.message.answer(f"{user_data.get('pd2')}", reply_markup = keyboard)
            await state.set_state(UserState.pd2)
            await callback_query.answer()
    else:
         await state.set_state(UserState.pd5)
         await q1(callback_query, state)



@router.callback_query(StateFilter(UserState.pd2))
async def pd3(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('pd3')
    if text:
        match = re.search(TELEGRAM_VIDEO_PATTERN, user_data.get('video_3'))
        if match:           
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
            await callback_query.message.answer_video(video=user_data.get('video_3'))
            await callback_query.message.answer(text=f"{user_data.get('pd3')}", reply_markup = keyboard)
            await state.set_state(UserState.pd3)
            await callback_query.answer()
        else: 
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
            await callback_query.message.answer(f"{user_data.get('pd3')}", reply_markup = keyboard)
            await state.set_state(UserState.pd3)
            await callback_query.answer()
    else:
         await state.set_state(UserState.pd5)
         await q1(callback_query, state)



@router.callback_query(StateFilter(UserState.pd3))
async def pd4(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('pd4')
    if text:
        match = re.search(TELEGRAM_VIDEO_PATTERN, user_data.get('video_4'))
        if match:           
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
            await callback_query.message.answer_video(video=user_data.get('video_4'))
            await callback_query.message.answer(text=f"{user_data.get('pd4')}", reply_markup = keyboard)
            await state.set_state(UserState.pd4)
            await callback_query.answer()
        else:
        
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
            await callback_query.message.answer(f"{user_data.get('pd4')}", reply_markup = keyboard)
            await state.set_state(UserState.pd4)
            await callback_query.answer()
    else:
         await state.set_state(UserState.pd5)
         await q1(callback_query, state)
    


@router.callback_query(StateFilter(UserState.pd4))
async def pd5(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('pd5')
    if text:
        match = re.search(TELEGRAM_VIDEO_PATTERN, user_data.get('video_5'))
        if match:           
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
            await callback_query.message.answer_video(video=user_data.get('video_5'))
            await callback_query.message.answer(text=f"{user_data.get('pd5')}", reply_markup = keyboard)
            await state.set_state(UserState.pd5)
            await callback_query.answer()
        else:
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Продолжить", callback_data="next")]
            ])
            await callback_query.message.answer(f"{user_data.get('pd5')}", reply_markup = keyboard)
            await state.set_state(UserState.pd5)
            
            await callback_query.answer()
    else:
         await state.set_state(UserState.pd5)
         await q1(callback_query, state)





@router.callback_query(StateFilter(UserState.pd5))
async def q1(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    text = user_data.get('text_1')
    text_2 = user_data.get('q1')
    if text and text_2:
        await callback_query.message.answer(f"{text}")
        await callback_query.answer()
        await callback_query.message.answer(f"{user_data.get('q1')}")
        await state.set_state(UserState.q1)
    else:
        await state.update_data(survey_completed = True)
        await state.set_state(UserState.result_yes)
        await bot.send_message(chat_id=callback_query.message.chat.id, text="Пожалуйста напишите ваше ФИО.")


@router.message(StateFilter(UserState.q1))
async def q2(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans1=ans1)
    user_data = await state.get_data()
    text = user_data.get('q2')
    if text:
        await message.answer(f"{user_data.get('q2')}")
        await state.set_state(UserState.q2)
    else:
        await state.set_state(UserState.q10)
        await process_answers(message, state)

@router.message(StateFilter(UserState.q2))
async def q3(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans2=ans1)
    user_data = await state.get_data()
    text = user_data.get('q3')
    if text:
        await message.answer(f"{user_data.get('q3')}")
        await state.set_state(UserState.q3)
    else:
        await state.set_state(UserState.q10)
        await process_answers(message, state)

@router.message(StateFilter(UserState.q3))
async def q4(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans3=ans1)
    user_data = await state.get_data()
    text = user_data.get('q4')
    if text:
        await message.answer(f"{user_data.get('q4')}")
        await state.set_state(UserState.q4)
    else:
        await state.set_state(UserState.q10)
        await process_answers(message, state)

@router.message(StateFilter(UserState.q4))
async def q5(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans4=ans1)
    user_data = await state.get_data()
    text = user_data.get('q5')
    if text:
        await message.answer(f"{user_data.get('q5')}")
        await state.set_state(UserState.q5)
    else:
        await state.set_state(UserState.q10)
        await process_answers(message, state)

@router.message(StateFilter(UserState.q5))
async def q6(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans5=ans1)
    user_data = await state.get_data()
    text = user_data.get('q6')
    if text:
        await message.answer(f"{user_data.get('q6')}")
        await state.set_state(UserState.q6)
    else:
        await state.set_state(UserState.q10)
        await process_answers(message, state)    

@router.message(StateFilter(UserState.q6))
async def q7(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans6=ans1)
    user_data = await state.get_data()
    text = user_data.get('q7')
    if text:
        await message.answer(f"{user_data.get('q7')}")
        await state.set_state(UserState.q7)
    else:
        await state.set_state(UserState.q10)
        await process_answers(message, state)

@router.message(StateFilter(UserState.q7))
async def q8(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans7=ans1)
    user_data = await state.get_data()
    text = user_data.get('q8')
    if text:
        await message.answer(f"{user_data.get('q8')}")
        await state.set_state(UserState.q8)
    else:
        await state.set_state(UserState.q10)
        await process_answers(message, state)

@router.message(StateFilter(UserState.q8))
async def q9(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans8=ans1)
    user_data = await state.get_data()
    text = user_data.get('q9')
    if text:
        await message.answer(f"{user_data.get('q9')}")
        await state.set_state(UserState.q9)
    else:
        await state.set_state(UserState.q10)
        await process_answers(message, state)

@router.message(StateFilter(UserState.q9))
async def q10(message: Message, state: FSMContext):
    ans1 = message.text
    await state.update_data(ans9=ans1)
    user_data = await state.get_data()
    text = user_data.get('q10')
    if text:
        await message.answer(f"{user_data.get('q10')}")
        await state.set_state(UserState.q10)
    else:
        await state.set_state(UserState.q10)
        await process_answers(message, state)



@router.message(StateFilter(UserState.q10))
async def process_answers(message: Message, state: FSMContext):
    chat_id = message.chat.id
    user_data = await state.get_data()
    text = user_data.get('text_1')
    
    if message.video:
        video = message.video.file_id
        transcript_text = await handle_transcript(bot, video, is_video=True)
        await state.update_data(video=video, transcript=transcript_text)
        await message.answer("Подтвердить это видео? Для подтверждения нажмите на кнопку ниже или напишите в чат \"Подтвердить\"", 
                          reply_markup=ReplyKeyboardMarkup(
                              keyboard=[
                                  [KeyboardButton(text="Подтвердить")],
                                  [KeyboardButton(text="Записать новое")]
                              ],
                              resize_keyboard=True
                          ))
        return
    
    elif message.video_note:
        video_note = message.video_note.file_id
        transcript_text = await handle_transcript(bot, video_note, is_video=True)
        await state.update_data(video_note=video_note, transcript=transcript_text)
        await message.answer("Подтвердить это видео? Для подтверждения нажмите на кнопку ниже или напишите в чат \"Подтвердить\"", 
                          reply_markup=ReplyKeyboardMarkup(
                              keyboard=[
                                  [KeyboardButton(text="Подтвердить")],
                                  [KeyboardButton(text="Записать новое")]
                              ],
                              resize_keyboard=True
                          ))
        return
    
    elif message.audio:
        audio = message.audio.file_id
        transcript_text = await handle_transcript(bot, audio)
        await state.update_data(audio=audio, transcript=transcript_text)
        await message.answer("Подтвердить это аудио? Для подтверждения нажмите на кнопку ниже или напишите в чат \"Подтвердить\"", 
                          reply_markup=ReplyKeyboardMarkup(
                              keyboard=[
                                  [KeyboardButton(text="Подтвердить")],
                                  [KeyboardButton(text="Записать новое")]
                              ],
                              resize_keyboard=True
                          ))
        return
    
    elif message.voice:
        voice = message.voice.file_id
        transcript_text = await handle_transcript(bot, voice)
        await state.update_data(voice=voice, transcript=transcript_text)
        await message.answer("Подтвердить это аудио? Для подтверждения нажмите на кнопку ниже или напишите в чат \"Подтвердить\"", 
                          reply_markup=ReplyKeyboardMarkup(
                              keyboard=[
                                  [KeyboardButton(text="Подтвердить")],
                                  [KeyboardButton(text="Записать новое")]
                              ],
                              resize_keyboard=True
                          ))
        return
    
    elif message.text:  
        if message.text == "Подтвердить" or message.text == "подтвердить":
            ans10 = "Кандидат отправил медиафайл"
            await state.update_data(ans10=ans10)

        elif message.text == "Записать новое":
            await message.answer("Отправьте новое медиа", reply_markup=ReplyKeyboardRemove())
            return
        else:
            ans10 = message.text
            await state.update_data(ans10=ans10)
    else:
        ans10 = "Неизвестный формат сообщения"
        await state.update_data(ans10=ans10)
    user_data = await state.get_data()
    text = user_data.get('text_2')
    await message.answer(f"{text}", reply_markup=ReplyKeyboardRemove())
    await state.update_data(survey_completed=True)
    
    user_data = await state.get_data()
    sheet_id = user_data.get('sheet_id')
    transcript_text = user_data.get('transcript')
   
    user_data = await state.get_data()
    if transcript_text:
        await state.update_data(ans10=transcript_text)
        user_qa = f"Вопрос 1: {user_data.get('q1')}, ответ: {user_data.get('ans1')}; Вопрос 2: {user_data.get('q2')}, ответ: {user_data.get('ans2')}; Вопрос 3: {user_data.get('q3')}, ответ: {user_data.get('ans3')}; Вопрос 4: {user_data.get('q4')}, ответ: {user_data.get('ans4')}; Вопрос 5: {user_data.get('q5')}, ответ: {user_data.get('ans5')}; Вопрос 6: {user_data.get('q6')}, ответ: {user_data.get('ans6')}; Вопрос 7:{user_data.get('q7')}, ответ: {user_data.get('ans7')}; Вопрос 8: {user_data.get('q8')}, ответ: {user_data.get('ans8')}; Вопрос 9: {user_data.get('q9')}, ответ: {user_data.get('ans9')}; Вопрос 10:{user_data.get('q10')}, ответ: {user_data.get('transcript')}"
        promt = f"Ты HR менеджер с опытом более 30 лет в найме, поиске и обучении персонала, с учетом всего своего опыта, чтобы в будущем подобрать кандидата для нашей вакансии: {user_data.get('job_name')}, тебе надо дать оценку ответам на вопросы по стобальной шкале и выдать общий балл по кандидату. Не нужно давать комментарий или писать любые буквы, нужно строго только одно число с общим баллом. (Обязательно без спецсимволов, например точки). Для принятия решения сравни текст вакансии {user_data.get('job_text')}, портрет кандидата {user_data.get('portrait')} и вопросы и ответы пользователя который надо оценить и написать. Вопрос 1: {user_data.get('q1')}, ответ 1: {user_data.get('ans1')}; Вопрос 2: {user_data.get('q2')}, ответ 2: {user_data.get('ans2')}; Вопрос 3: {user_data.get('q3')}, ответ 3: {user_data.get('ans3')}; Вопрос 4: {user_data.get('q4')}, ответ 4: {user_data.get('ans4')}; Вопрос 5: {user_data.get('q5')}, ответ 5: {user_data.get('ans5')}; Вопрос 6: {user_data.get('q6')}, ответ 6: {user_data.get('ans6')}; Вопрос 7:{user_data.get('q7')}, ответ 7: {user_data.get('ans7')}; Вопрос 8: {user_data.get('q8')}, ответ 8: {user_data.get('ans8')}; Вопрос 9: {user_data.get('q9')}, ответ 9: {user_data.get('ans9')}; Вопрос 10:{user_data.get('q10')}, ответ 10: {user_data.get('transcript')}. Дополнительно если в тексте меньше 10 вопросов, то последний ответ будет для крайнего вопроса"
        promt_2 = f"Ты HR менеджер с опытом более 30 лет в найме, поиске и обучении персонала, с учетом всего своего опыта, чтобы в будущем подобрать идеального кандидата для нашей вакансии: {user_data.get('job_name')}, тебе надо оценить кандидата, сравнить его с вакансией и написать комментарии что ты считаешь по нему. Вот вопросы и ответы пользователя который надо оценить и написать свои комментарии по кандидату строго до 1000 символов: Вопрос 1: {user_data.get('q1')}, ответ 1: {user_data.get('ans1')}; Вопрос 2: {user_data.get('q2')}, ответ 2: {user_data.get('ans2')}; Вопрос 3: {user_data.get('q3')}, ответ 3: {user_data.get('ans3')}; Вопрос 4: {user_data.get('q4')}, ответ 4: {user_data.get('ans4')}; Вопрос 5: {user_data.get('q5')}, ответ 5: {user_data.get('ans5')}; Вопрос 6: {user_data.get('q6')}, ответ 6: {user_data.get('ans6')}; Вопрос 7:{user_data.get('q7')}, ответ 7: {user_data.get('ans7')}; Вопрос 8: {user_data.get('q8')}, ответ 8: {user_data.get('ans8')}; Вопрос 9: {user_data.get('q9')}, ответ 10: {user_data.get('ans9')}; Вопрос 10:{user_data.get('q10')}, ответ 10: {user_data.get('transcript')} Вот текст вакансии для анализа {user_data.get('job_text')} и портрет кандидата {user_data.get('portrait')}. Дополнительно если в тексте меньше 10 вопросов, то последний ответ будет для крайнего вопроса"
    
    else:    
        user_qa = f"Вопрос 1: {user_data.get('q1')}, ответ: {user_data.get('ans1')}; Вопрос 2: {user_data.get('q2')}, ответ: {user_data.get('ans2')}; Вопрос 3: {user_data.get('q3')}, ответ: {user_data.get('ans3')}; Вопрос 4: {user_data.get('q4')}, ответ: {user_data.get('ans4')}; Вопрос 5: {user_data.get('q5')}, ответ: {user_data.get('ans5')}; Вопрос 6: {user_data.get('q6')}, ответ: {user_data.get('ans6')}; Вопрос 7:{user_data.get('q7')}, ответ: {user_data.get('ans7')}; Вопрос 8: {user_data.get('q8')}, ответ: {user_data.get('ans8')}; Вопрос 9: {user_data.get('q9')}, ответ: {user_data.get('ans9')}; Вопрос 10:{user_data.get('q10')}, ответ: {user_data.get('ans10')}"
        promt = f"Ты HR менеджер с опытом более 30 лет в найме, поиске и обучении персонала, с учетом всего своего опыта, чтобы в будущем подобрать кандидата для нашей вакансии: {user_data.get('job_name')}, тебе надо дать оценку ответам на вопросы по стобальной шкале и выдать общий балл по кандидату. Не нужно давать комментарий или писать любые буквы, нужно строго только одно число с общим баллом. (Обязательно без спецсимволов, например точки). Для принятия решения сравни текст вакансии {user_data.get('job_text')}, портрет кандидата {user_data.get('portrait')} и вопросы и ответы пользователя который надо оценить и написать. Вопрос 1: {user_data.get('q1')}, ответ 1: {user_data.get('ans1')}; Вопрос 2: {user_data.get('q2')}, ответ 2: {user_data.get('ans2')}; Вопрос 3: {user_data.get('q3')}, ответ 3: {user_data.get('ans3')}; Вопрос 4: {user_data.get('q4')}, ответ 4: {user_data.get('ans4')}; Вопрос 5: {user_data.get('q5')}, ответ 5: {user_data.get('ans5')}; Вопрос 6: {user_data.get('q6')}, ответ 6: {user_data.get('ans6')}; Вопрос 7:{user_data.get('q7')}, ответ 7: {user_data.get('ans7')}; Вопрос 8: {user_data.get('q8')}, ответ 8: {user_data.get('ans8')}; Вопрос 9: {user_data.get('q9')}, ответ 9: {user_data.get('ans9')}; Вопрос 10:{user_data.get('q10')}, ответ 10: {user_data.get('ans10')}. Дополнительно если в тексте меньше 10 вопросов, то последний ответ будет для крайнего вопроса"
        promt_2 = f"Ты HR менеджер с опытом более 30 лет в найме, поиске и обучении персонала, с учетом всего своего опыта, чтобы в будущем подобрать идеального кандидата для нашей вакансии: {user_data.get('job_name')}, тебе надо оценить кандидата, сравнить его с вакансией и написать комментарии что ты считаешь по нему. Вот вопросы и ответы пользователя который надо оценить и написать свои комментарии по кандидату строго до 1000 символов: Вопрос 1: {user_data.get('q1')}, ответ 1: {user_data.get('ans1')}; Вопрос 2: {user_data.get('q2')}, ответ 2: {user_data.get('ans2')}; Вопрос 3: {user_data.get('q3')}, ответ 3: {user_data.get('ans3')}; Вопрос 4: {user_data.get('q4')}, ответ 4: {user_data.get('ans4')}; Вопрос 5: {user_data.get('q5')}, ответ 5: {user_data.get('ans5')}; Вопрос 6: {user_data.get('q6')}, ответ 6: {user_data.get('ans6')}; Вопрос 7:{user_data.get('q7')}, ответ 7: {user_data.get('ans7')}; Вопрос 8: {user_data.get('q8')}, ответ 8: {user_data.get('ans8')}; Вопрос 9: {user_data.get('q9')}, ответ 10: {user_data.get('ans9')}; Вопрос 10:{user_data.get('q10')}, ответ 10: {user_data.get('ans10')} Вот текст вакансии для анализа {user_data.get('job_text')} и портрет кандидата {user_data.get('portrait')}. Дополнительно если в тексте меньше 10 вопросов, то последний ответ будет для крайнего вопроса"
    
    response_score = await get_chatgpt_response(promt)
    response_2 = await get_chatgpt_response(promt_2)
    target_score = user_data.get('score')
    if int(response_score) >= int(target_score):
        response = "2.Собеседование"
    else:
        response = "3.Отказ"
    gpt_response = f"Баллы кандидата: {response_score}\n\n AI комментарий: {response_2}"     
    await state.update_data(response=response, 
                            response_2=response_2,
                            user_qa = user_qa,
                            response_score=response_score,
                            gpt_response=gpt_response
                            )
    # await message.answer(f"{response_score}\n\n{response}\n\n {response_2}")
    company_name = user_data.get('company_name')
    job_name = user_data.get('job_name')
        
    if response == "2.Собеседование":
        await state.set_state(UserState.result_yes)
        await write_to_google_sheet(
            sheet_id = sheet_id, 
            username = message.from_user.username,
            first_name=message.from_user.first_name,
            status=response,
            gpt_response=gpt_response,
            qa_data=user_qa,
            company_name = company_name,
            job_name = job_name,
            user_score=response_score,
            chat_id=chat_id
            )
        text_3 = user_data.get('text_3')
        await message.answer(text=text_3)
        await message.answer("Пожалуйста напишите ваше ФИО.")
    
    
    
    elif response == "3.Отказ":
        await state.set_state(UserState.result_no)
        await message.answer(f"{user_data.get('text_4')}") 
        # Записываем в таблицу
        await write_to_google_sheet(
        sheet_id=sheet_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        status=response,  
        gpt_response=gpt_response,
        qa_data=user_qa,
        company_name = company_name,
        job_name = job_name,
        user_score=response_score,
        chat_id=chat_id
        )
    
          
          
@router.message(StateFilter(UserState.result_yes))
async def process_name(message: Message, state: FSMContext):
        user_fio = message.text
        await state.update_data(user_fio=user_fio)
        await state.set_state(UserState.user_resume)
        await message.answer("Пришлите, пожалуйста, ссылку на ваше резюме.\n\nВзять на резюме ссылку можно по следующей ссылке: https://hh.ru/applicant/resumes")

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
                await message.answer("Нет доступного времени")



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
        await callback.message.edit_text(
            "Доступное время для записи:",
            reply_markup=keyboard
        )
        await state.set_state(UserState.slot_time)
    else:
        await callback.answer("К сожалению, на этот день нет свободного времени.")
    
    await callback.answer()



@router.callback_query(lambda c: c.data.startswith("select_time_"), UserState.slot_time)
async def process_time_selection(callback: CallbackQuery, state: FSMContext, pool: asyncpg.Pool):
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
        await state.update_data(target_cell = target_cell)

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
        
        # 6. Получаем время для отображения пользователю (асинхронно)
        time_value = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: sheet.acell(f'A{row_number}').value
        )
        date_value = await asyncio.get_event_loop().run_in_executor(
             None,
            lambda: sheet.acell(f'{column_letter}3').value
        )
        
        

        # 7. Подготовка данных для записи
        record_text = (
            f"{date_value} {time_value} #{user_data.get('response')}\n\n"
            f"Компания: {user_data.get('company_name')}\n"
            f"Вакансия: {user_data.get('job_name')}\n\n"
            f"ФИО: {user_data.get('user_fio', 'Без имени')}\n"
            f"ТГ: @{callback.from_user.username}\n"
            f"Ссылка на переписку: https://t.me/{callback.from_user.username}\n"
            f"Номер: {user_data.get('user_phone', 'Без телефона')}\n"
            f"Резюме: {user_data.get('user_resume')}\n"
            f"Cылка на таблицу: https://docs.google.com/spreadsheets/d/{user_data.get('sheet_id')}\n\n"
            f"Баллы кандидата: {user_data.get('response_score')}\n\n"
            f"AI комментарий: {user_data.get('response_2')}"
            
        )
        
        await state.update_data(time_value=time_value, 
                            date_value=date_value
                            )
        
        # 8. Запись в таблицу (асинхронно)
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: sheet.update(
                range_name=target_cell,
                values=[[record_text]],
                value_input_option='USER_ENTERED'
            )
        )
        
        
        keyboard =  InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Изменить время", callback_data="change_time")],
                [InlineKeyboardButton(text="Удалить запись", callback_data="delete_time")]
                ])
        user_data = await state.get_data()
        # 9. Отправляем подтверждение пользователю
        await callback.message.edit_text(
            f"Ждем Вас в {date_value} в {time_value} на собеседование\n\n"
            f"{user_data.get('text_5')}", reply_markup=keyboard
        )

        user_chat_id = callback.message.chat.id
        chat_id = user_data.get('chat_id')
        sheet_range = user_data.get('sheet_range')
        await state.set_state(UserState.process_time_change)
        decline_text=user_data.get('decline_text')
        learn_text=user_data.get('learn_text')
        practice_text=user_data.get('practice_text')
        accept_text=user_data.get('accept_text')
        candidate_chat_id = callback.message.chat.id
        
        action_keyboard = await get_action_keyboard(
                                                pool=pool,
                                                column_letter=column_letter,
                                                row_number=row_number,
                                                candidate_chat_id=str(candidate_chat_id),
                                                sheet_id=sheet_id,
                                                sheet_range=sheet_range,
                                                decline_text=decline_text,
                                                learn_text=learn_text,
                                                practice_text=practice_text,
                                                accept_text=accept_text
                                            )
        await bot.send_message(chat_id=chat_id,
                                text=f"{record_text}",
                                reply_markup=action_keyboard,
                                disable_web_page_preview=True
                                )
        video = user_data.get('video')
        if video:
            await bot.send_video(chat_id=chat_id,
                                video=video,
                                caption="Видео от кандидата"
                                )
        
        video_note = user_data.get('video_note')
        if video_note:
            await bot.send_video_note(chat_id=chat_id,
                                video_note=video_note
                                )
        audio = user_data.get('audio')
        if audio:
             await bot.send_audio(chat_id = chat_id,
                                  audio = audio)
        voice = user_data.get('voice')
        if voice:
            await bot.send_voice(chat_id = chat_id,
                                 voice = voice)
        transcript_text = user_data.get('transcript')
        if transcript_text:
            await bot.send_message(chat_id=chat_id,
                                   text=transcript_text)
        # 10. Сохраняем данные в Google Sheets (асинхронно)
        success = await write_to_google_sheet(
            sheet_id=sheet_id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
            status="2.Собеседование",
            gpt_response=user_data.get('gpt_response', ''),
            full_name=user_data.get('user_fio'),
            phone_number=user_data.get('user_phone'),
            resume_link=user_data.get('user_resume'),
            interview_date=date_value,
            interview_time=time_value,
            qa_data=user_data.get('user_qa'),
            job_name=user_data.get('job_name'),
            company_name=user_data.get('company_name'),
            user_score=user_data.get('response_score'),
            chat_id=user_chat_id
        )
        
        user_data = await state.get_data()
        interview_time = parse_interview_datetime(date_value, time_value)
        interview_time_utc = interview_time.astimezone(SERVER_TZ)
        task1 = asyncio.create_task(send_reminder_at_time(callback.message.chat.id, interview_time_utc - timedelta(hours=1), f"{user_data.get('text_7')}"))
        task2 = asyncio.create_task(send_reminder_at_time(callback.message.chat.id, interview_time_utc, f"{user_data.get('text_8')}"))
        
        await state.update_data(
        date_value=date_value,
        time_value=time_value,
        reminder_tasks=[id(task1), id(task2)]  # Список ID задач
        )
        if not success:
            await callback.message.answer("⚠️ Ошибка сохранения данных в таблицу")
        
        
        
    except Exception as e:
        logging.error(f"Ошибка записи: {str(e)}", exc_info=True)
        await callback.answer("⚠️ Ошибка сервера, попробуйте позже", show_alert=True)


@router.callback_query(StateFilter(UserState.process_time_change))
async def time_change(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == "change_time":
        user_data = await state.get_data()
        sheet_id = user_data.get('sheet_id')
        target_cell = user_data.get('target_cell')
        await clear_cell(sheet_id, target_cell)
        await state.set_state(UserState.slot_day)
         
        # Получаем sheet_id из состояния или базы данных
        user_data = await state.get_data()
        sheet_id = user_data.get('sheet_id')
        
        # Получаем клавиатуру с кнопками
        keyboard = await check_empty_cells(sheet_id)
        
        if keyboard:
                await callback_query.message.answer(
                "Выберите дату для записи",
                reply_markup=keyboard
                )
                
        else:
                await callback_query.message.answer("Нет доступного времени")

        await callback_query.answer()

    elif callback_query.data == "delete_time":
        user_data = await state.get_data()
        sheet_id = user_data.get('sheet_id')
        target_cell = user_data.get('target_cell')
        
        await  clear_cell(sheet_id, target_cell)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Новая запись", callback_data="change_time")]
        ])

        await callback_query.message.answer("Запись успешно удалена!", reply_markup = keyboard)

        await callback_query.answer()
    










##########################################################################################################################################################################################################


async def get_action_keyboard(
    pool: asyncpg.Pool,
    *,
    column_letter: str,
    row_number: int,
    candidate_chat_id: int,
    sheet_id: str,
    sheet_range: str,
    decline_text: str,
    learn_text: str,
    practice_text: str,
    accept_text: str
) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру с действиями для кандидата"""
    action_id = await save_action_to_db(
        pool=pool,
        column_letter=column_letter,
        row_number=row_number,
        candidate_chat_id=candidate_chat_id,
        sheet_id=sheet_id,
        sheet_range=sheet_range,
        decline_text=decline_text,
        learn_text=learn_text,
        practice_text=practice_text,
        accept_text=accept_text
    )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Отказать",
                    callback_data=f"decline_{action_id}"
                )
            ],
            [ 
                InlineKeyboardButton(
                    text="❌ Отказать и удалить из календаря", 
                    callback_data=f"delete_{action_id}" 
                )
            ],
            [ 
                InlineKeyboardButton(
                    text="✅ Отправить на обучение", 
                    callback_data=f"learn_{action_id}"
                )
            ],
            [  
                InlineKeyboardButton(
                    text="✅ Отправить на стажировку", 
                    callback_data=f"practice_{action_id}"
                )
            ],
            [  
                InlineKeyboardButton(
                    text="✅ Пригласить на работу", 
                    callback_data=f"accept_{action_id}"
                )
            ]
        ]
    )


@router.callback_query(F.data.startswith(("decline_", "learn_", "practice_", "accept_", "delete_")))
async def handle_actions(callback: CallbackQuery, bot: Bot, pool: asyncpg.Pool):
    action_prefix, action_id_str = callback.data.split("_", 1)
    action_id = int(action_id_str)
    
    async with pool.acquire() as conn:
        data = await conn.fetchrow(
            "SELECT * FROM candidate_actions WHERE action_id = $1", 
            action_id
        )
    
    if not data:
        return await callback.answer("Действие не найдено")
    
    chat_id = data['candidate_chat_id']
    column_letter = data['column_letter']
    row_number = data['row_number']
    decline_text = data['decline_text']
    learn_text = data['learn_text']
    practice_text = data['practice_text']
    accept_text = data['accept_text']
    sheet_id = data['sheet_id']

    if action_prefix == "decline":
        await bot.send_message(chat_id=chat_id,
                               text=decline_text)
        await callback.message.reply("Отказ отправлен кандидату")
    elif action_prefix == "delete":
        cell_range = f"{column_letter}{row_number}"
        await clear_cell(sheet_id, cell_range)
        await bot.send_message(chat_id=chat_id,
                               text=decline_text)
        await callback.message.reply("Отказ отправлен кандидату, запись из таблицы удалена")
    elif action_prefix == "learn":
        await bot.send_message(chat_id=chat_id,
                               text=learn_text)
        await callback.message.reply("Приглашение на обучение отправлено")
    elif action_prefix == "practice":
        await bot.send_message(chat_id=chat_id,
                               text=practice_text)
        await callback.message.reply("Приглашение на стажировку отправлено")
    elif action_prefix == "accept":
        await bot.send_message(chat_id=chat_id,
                               text=accept_text)
        await callback.message.reply("Приглашение на работу отправлено")
    
    
    
    
##########################################################################################################################################################################################################
async def check_survey_completion(chat_id: int, state: FSMContext):
    await asyncio.sleep(3600)  # Ждем 1 час
    
    data = await state.get_data()
    if not data.get("survey_completed", False):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Продолжить", callback_data="notification")]
        ])
        await bot.send_message(chat_id, f"{data.get('text_6')}",reply_markup=keyboard)


async def send_reminder(chat_id: int, text: str):
    await bot.send_message(chat_id, text)


async def send_reminder_at_time(chat_id: int, time_utc: datetime, text: str):
    delay = (time_utc - datetime.now(SERVER_TZ)).total_seconds()
    if delay > 0:
        await asyncio.sleep(delay)
        await send_reminder(chat_id, text)


async def cancel_old_reminders(state: FSMContext):
    data = await state.get_data()
    if "reminder_tasks" in data:
        for task_id in data["reminder_tasks"]:
            task = asyncio.all_tasks().get(task_id)
            if task and not task.done():
                task.cancel()

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
    pool = await get_async_connection()
    dp["pool"] = pool
    
    
    async def get_pool(dispatcher: Dispatcher) -> asyncpg.Pool:
        return dispatcher["pool"]
    
    dp["dependency_overrides"] = {asyncpg.Pool: get_pool}

    try:
        await dp.start_polling(bot)
    finally:
        await pool.close()
        print("Отключаюсь от БД")

if __name__ == "__main__":
    asyncio.run(main())