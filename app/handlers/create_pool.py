from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.utils import deep_linking
from aiogram.utils.callback_data import CallbackData

from app.db import db_create_pool, db_create_answer, db_is_respondent
from app.handlers.start import OrderAnswer, sending_a_created

pool_cb = CallbackData("pool", "action")


# Создание опроса
async def create_pool(message: Message):
    await message.answer("Напишите текст опроса.\n"
                         "Бывают люди, которым «хочется возразить», а что, как, почему, зачем, это им не дано!",
                         reply_markup=ReplyKeyboardRemove())
    await OrderAnswer.waiting_for_question.set()


async def wait_question(message: Message, state: FSMContext):
    await message.answer("Напишите текст ответа №1")
    await OrderAnswer.next()
    async with state.proxy() as state_proxy:
        state_proxy['question'] = message.text
        state_proxy['numbers'] = 0
        state_proxy['answer_3'] = None
        state_proxy['answer_4'] = None
        state_proxy['answer_5'] = None
        state_proxy['answer_6'] = None


async def wait_answer(message: Message, state: FSMContext):
    async with state.proxy() as state_proxy:
        state_proxy['numbers'] += 1

    ans = "Напишите текст ответа №" + str(
        state_proxy['numbers'] + 1) + "\n" + "\nЕсли ответов не осталось, то введите команду /finish"
    if state_proxy['numbers'] == 1:
        await message.answer("Напишите текст ответа №2")
        await state.update_data(answer_1=message.text)
    elif state_proxy['numbers'] == 2:
        await message.answer(ans)
        await state.update_data(answer_2=message.text)
    elif state_proxy['numbers'] == 3:
        await message.answer(ans)
        await state.update_data(answer_3=message.text)
    elif state_proxy['numbers'] == 4:
        await message.answer(ans)
        await state.update_data(answer_4=message.text)
    elif state_proxy['numbers'] == 5:
        await message.answer(ans)
        await state.update_data(answer_5=message.text)
    elif state_proxy['numbers'] == 6:
        await state.update_data(answer_6=message.text)
        await send_poll(message, state)


async def send_poll(message: Message, state: FSMContext):
    state_data = await state.get_data()
    bol = await db_create_pool(message.from_user.id, state_data['numbers'], state_data['question'],
                               state_data['answer_1'],
                               state_data['answer_2'],
                               state_data['answer_3'], state_data['answer_4'], state_data['answer_5'],
                               state_data['answer_6'])
    if bol:
        list_answers = [state_data['answer_1'], state_data['answer_2'], state_data['answer_3'], state_data['answer_4'],
                        state_data['answer_5'], state_data['answer_6']]
        await sending_a_created(message, int(state_data['numbers']), str(state_data['question']), list_answers,
                                str(bol.id_poll))
        link = await deep_linking.get_start_link(bol.id_poll)
        await message.answer("Cсылка: " + link)
    else:
        await message.answer("Как какать?")
    await state.finish()


# Блок закончен

# Преждевременное окончание ввода ответов на опрос
async def finish_answer(message: Message, state: FSMContext):
    state_data = await state.get_data()
    try:
        if state_data['numbers'] < 2:
            keyboard = InlineKeyboardMarkup(resize_keyboard=True)
            keyboard.add(KeyboardButton(text="Продолжить", callback_data=pool_cb.new(action="resume")))
            keyboard.add(KeyboardButton(text="Потерять", callback_data=pool_cb.new(action="delete")))
            await message.answer("В опросе нельзя использовать меньше 2 ответов, вы хотите потерять все данные?",
                                 reply_markup=keyboard)
        else:
            await send_poll(message, state)
    except:
        return


async def resume_pool(call: CallbackQuery):
    await call.message.delete()
    await call.bot.delete_message(call.message.chat.id, call.message.message_id - 1)


async def delete_pool(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.message.answer("Вы прервали создание запроса. Данные потеряны!")


# Блок закончен


# Создание ответа на опрос
async def call_back_answer(call: CallbackQuery, callback_data: dict):
    info = await db_is_respondent(int(callback_data["id_pool"]), call.from_user.id)
    if info == 0:
        await db_create_answer(int(callback_data["id_pool"]), call.from_user.id, int(callback_data["number"]))
        await call.message.edit_text("Выбран ответ №" + callback_data["number"])
    else:
        await call.message.edit_text("Ты думал я не узнаю что ты голосуешь 2 раз?!\n Пососи, туц туц туц")

# Блок закончен
