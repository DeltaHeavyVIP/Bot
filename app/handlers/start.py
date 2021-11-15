from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, Message, InlineKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData

from app.db import db_get_pool, db_is_respondent

answer_cb = CallbackData("answer", "id_pool", "number")


class OrderAnswer(StatesGroup):
    waiting_for_question = State()
    waiting_for_answer = State()


async def start(message: Message, state: FSMContext):
    await state.finish()
    spl = message.text.split()
    if len(spl) == 1:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("Создать опрос", "Статистика опросов")
        await message.answer("Я бот коммунист! \n"
                             "Хочешь посмотерть опрос или создать его?", reply_markup=keyboard)
    elif len(spl) == 2:
        info = await db_is_respondent(int(spl[1]), message.from_user.id)
        if info == 0:
            try:
                count_answers, question, list_answer = await db_get_pool(int(spl[1]))
            except:
                await message.answer("Такого опроса не существует!")
                return
            await sending_a_created(message, count_answers, question, list_answer, spl[1])
        else:
            await message.answer("Вы уже проходили этот опрос!")


async def sending_a_created(message: Message, count_answers: int, question: str, list_answer: list, id_poll: str):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for i in range(1, count_answers):
        keyboard.add(KeyboardButton(text=list_answer[i - 1], callback_data=answer_cb.new(id_pool=id_poll, number=i)))
    await message.answer(question, reply_markup=keyboard)
