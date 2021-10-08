from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, Message, ReplyKeyboardRemove, InlineKeyboardMarkup, KeyboardButton, \
    CallbackQuery
from aiogram.utils import deep_linking

from app.db import db_create_pool, db_create_answer


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
                               state_data['answer_3'], state_data['answer_4'], state_data['answer_5'], state_data['answer_6'])
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


async def call_back_answer(call: CallbackQuery):
    await db_create_answer(call.message.message_id, call.from_user.id, int(call.data[-1]))
    await call.message.edit_text("Ответ отправлен", reply_markup=ReplyKeyboardRemove())


def register_handlers_start(dp: Dispatcher):
    dp.register_message_handler(start, commands="start", state="*")
    dp.register_message_handler(create_pool, Text(equals="Создать опрос", ignore_case=True), state="*")
    dp.register_message_handler(wait_question, state=OrderAnswer.waiting_for_question)
    dp.register_message_handler(wait_answer, state=OrderAnswer.waiting_for_answer)

    dp.register_callback_query_handler(call_back_answer, Text(startswith="answer_"), state="*")