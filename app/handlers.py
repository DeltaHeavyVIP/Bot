from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, Message, ReplyKeyboardRemove, InlineKeyboardMarkup, KeyboardButton, \
    CallbackQuery
from aiogram.utils import deep_linking

from app.db import db_create_pool, db_start, db_close_connections, db_create_answer


class OrderAnswer(StatesGroup):
    waiting_for_question = State()
    waiting_for_answer = State()


async def start(message: Message, state: FSMContext):
    await state.finish()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Создать опрос", "Статистика опроса")
    await message.answer("Я бот коммунист! \n"
                         "Хочешь посмотерть опрос или создать его?", reply_markup=keyboard)


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


async def wait_answer(message: Message, state: FSMContext):
    state_data = await state.get_data()
    answer_numb = state_data['numbers']

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
        await send_poll(message, state)


async def send_poll(message: Message, state: FSMContext):
    state_data = await state.get_data()
    await db_start()
    bol = await db_create_pool(message.from_user.id, state_data['question'], state_data['answer_1'],
                               state_data['answer_2'],
                               state_data['answer_3'], state_data['answer_4'], state_data['answer_5'], message.text)
    await db_close_connections()
    if bol:
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        for i in range(0, state_data['numbers']):
            answer = "answer_" + str(i)
            keyboard.add(KeyboardButton(text=state_data[answer], callback_data=answer))
        await message.answer(state_data['question'],
                             reply_markup=keyboard)
        link = await deep_linking.get_start_link(message.message_id + 1)
        await message.answer("Cсылка: " + link)
    else:
        await message.answer("Как какать?")


async def call_back_answer(call: CallbackQuery, state: FSMContext):
    await db_start()
    await db_create_answer(call.message.message_id, call.from_user.id, int(call.data[-1]))
    await db_close_connections()
