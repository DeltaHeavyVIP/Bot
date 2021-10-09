from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, Message, ReplyKeyboardRemove, InlineKeyboardMarkup, KeyboardButton, \
    CallbackQuery
from aiogram.utils import deep_linking

from app.db import db_create_pool, db_create_answer, get_owner_polls


class OrderAnswer(StatesGroup):
    waiting_for_question = State()
    waiting_for_answer = State()


async def start(message: Message, state: FSMContext):
    await state.finish()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Создать опрос", "Статистика опросов")
    await message.answer("Я бот коммунист! \n"
                         "Хочешь посмотерть опрос или создать его?", reply_markup=keyboard)


# Создание опроса
async def create_pool(message: Message, state: FSMContext):
    await message.answer("Напишите текст опроса.\n"
                         "Бывают люди, которым «хочется возразить», а что, как, почему, зачем, это им не дано!",
                         reply_markup=ReplyKeyboardRemove())
    await OrderAnswer.waiting_for_question.set()


async def wait_question(message: Message, state: FSMContext):
    await state.update_data(question=message.text)
    await message.answer("Напишите текст ответа №1")
    await OrderAnswer.next()
    await state.update_data(numbers=1)
    await state.update_data(answer_3=None)
    await state.update_data(answer_4=None)
    await state.update_data(answer_5=None)
    await state.update_data(answer_6=None)


async def wait_answer(message: Message, state: FSMContext):
    state_data = await state.get_data()
    answer_numb = state_data['numbers']
    await state.update_data(numbers=answer_numb + 1)

    ans = "Напишите текст ответа №" + str(
        answer_numb + 1) + "\n" + "\nЕсли ответов не осталось, то введите команду /finish"
    if answer_numb == 1:
        await message.answer("Напишите текст ответа №2")
        await state.update_data(answer_1=message.text)
    elif answer_numb == 2:
        await message.answer(ans)
        await state.update_data(answer_2=message.text)
    elif answer_numb == 3:
        await message.answer(ans)
        await state.update_data(answer_3=message.text)
    elif answer_numb == 4:
        await message.answer(ans)
        await state.update_data(answer_4=message.text)
    elif answer_numb == 5:
        await message.answer(ans)
        await state.update_data(answer_5=message.text)
    elif answer_numb == 6:
        await state.update_data(answer_6=message.text)
        await send_poll(message, state)


async def send_poll(message: Message, state: FSMContext):
    state_data = await state.get_data()
    bol = await db_create_pool(message.from_user.id, state_data['question'], state_data['answer_1'],
                               state_data['answer_2'],
                               state_data['answer_3'], state_data['answer_4'], state_data['answer_5'],
                               state_data['answer_6'])
    if bol:
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        for i in range(1, state_data['numbers']):
            answer = "answer_" + str(i)
            keyboard.add(KeyboardButton(text=state_data[answer], callback_data=answer))
        await message.answer(state_data['question'],
                             reply_markup=keyboard)
        link = await deep_linking.get_start_link(message.message_id + 1)
        await message.answer("Cсылка: " + link)
    else:
        await message.answer("Как какать?")
    await state.finish()


# Блок закончен

# Создание ответа на опрос
async def call_back_answer(call: CallbackQuery):
    await db_create_answer(call.message.message_id, call.from_user.id,
                           int(call.data[-1]))  # TODO как получать id опроса
    await call.message.edit_text("Выбран ответ №" + call.data[-1])


# Блок закончен


# Преждевременное окончание ввода ответов на опрос
async def finish_answer(message: Message, state: FSMContext):
    state_data = await state.get_data()
    answer_numb = state_data['numbers']
    if answer_numb < 3:
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton(text="Продолжить", callback_data="resume_pool"))
        keyboard.add(KeyboardButton(text="Потерять", callback_data="delete_pool"))
        await message.answer("В опросе нельзя использовать меньше 2 ответов, вы хотите потерять все данные?",
                             reply_markup=keyboard)
    else:
        await send_poll(message, state)


async def resume_pool(call: CallbackQuery):
    await call.message.delete()
    await call.bot.delete_message(call.message.chat.id, call.message.message_id - 1)


async def delete_pool(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.message.answer("Вы прервали создание запроса. Данные потеряны!")


# Блок закончен
async def statistics_pool(message: Message, state: FSMContext):
    owner_polls: list = await get_owner_polls(message.from_user.id)
    await state.update_data(page=0)
    await state.update_data(owner_polls=owner_polls)
    await edit_message_statistics_pools(message, state)


async def next_statistics_poll(call: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    if state_data['page'] * 3 < len(state_data['owner_polls']):
        await state.update_data(page=(state_data['page'] + 1))
        await edit_message_statistics_pools(call.message, state)


async def last_statistics_poll(call: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    if state_data['page'] - 1 == 0:
        await statistics_pool(call.message, state)
    else:
        await state.update_data(page=(state_data['page'] - 1))
        await edit_message_statistics_pools(call.message, state)


async def edit_message_statistics_pools(message: Message, state: FSMContext):
    state_data = await state.get_data()
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(state_data['owner_polls']) % 3):
        keyboard.add(KeyboardButton(text=state_data['owner_polls'][state_data['page'] * 3 + i].question,
                                    callback_data="statistics_answer_" + str(i)))
    keyboard.add(KeyboardButton(text="<", callback_data="next"),
                 KeyboardButton(text=">", callback_data="last"))
    if state_data['page'] == 0:
        await message.answer("Ниже представлены ваши опросы.", reply_markup=keyboard)
    else:
        await message.edit_text("Ниже представлены ваши опросы.", reply_markup=keyboard)


# Регистрация хендлеров
def register_handlers_start(dp: Dispatcher):
    dp.register_message_handler(finish_answer, commands="finish")
    dp.register_callback_query_handler(resume_pool, lambda call: call.data == "resume_pool",
                                       state=OrderAnswer.waiting_for_answer)
    dp.register_callback_query_handler(delete_pool, lambda call: call.data == "delete_pool",
                                       state=OrderAnswer.waiting_for_answer)

    dp.register_message_handler(start, commands="start", state="*")
    dp.register_message_handler(create_pool, Text(equals="Создать опрос", ignore_case=True), state="*")
    dp.register_message_handler(wait_question, state=OrderAnswer.waiting_for_question)
    dp.register_message_handler(wait_answer, state=OrderAnswer.waiting_for_answer)
    dp.register_callback_query_handler(call_back_answer, Text(startswith="answer_"), state="*")

    dp.register_message_handler(statistics_pool, Text(equals="Статистика опросов", ignore_case=True), state="*")
    dp.register_callback_query_handler(next_statistics_poll, lambda call: call.data == "next", state="*")
    dp.register_callback_query_handler(last_statistics_poll, lambda call: call.data == "last", state="*")
