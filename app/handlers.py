from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, Message, ReplyKeyboardRemove, InlineKeyboardMarkup, KeyboardButton, \
    CallbackQuery
from aiogram.utils import deep_linking
from aiogram.utils.callback_data import CallbackData

from app.db import db_create_pool, db_create_answer, db_get_owner_polls, db_get_statistics_pool, db_get_pool, \
    db_is_respondent

pool_cb = CallbackData("pool", "action")
answer_cb = CallbackData("answer", "id_pool", "number")
statistics_answer_cb = CallbackData("statistics_answer", "id")

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
            await sending_a_created(message, count_answers, question, list_answer,spl[1])
        else:
            await message.answer("Вы уже проходили этот опрос!")


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
    bol = await db_create_pool(message.from_user.id, state_data['numbers'] - 1, state_data['question'],
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


async def sending_a_created(message: Message, count_answers: int, question: str, list_answer: list, id_poll: str):
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for i in range(1, count_answers):
        keyboard.add(KeyboardButton(text=list_answer[i - 1], callback_data=answer_cb.new(id_pool=id_poll, number=i)))
    await message.answer(question, reply_markup=keyboard)


# Блок закончен

# Создание ответа на опрос
async def call_back_answer(call: CallbackQuery, callback_data: dict):
    await db_create_answer(int(callback_data["id_pool"]), call.from_user.id, int(callback_data["number"]))
    await call.message.edit_text("Выбран ответ №" + callback_data["id_pool"])


# Блок закончен


# Преждевременное окончание ввода ответов на опрос
async def finish_answer(message: Message, state: FSMContext):
    state_data = await state.get_data()
    try:
        answer_numb = state_data['numbers']
    except:
        return
    if answer_numb < 3:
        keyboard = InlineKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton(text="Продолжить", callback_data=pool_cb.new(action="resume")))
        keyboard.add(KeyboardButton(text="Потерять", callback_data=pool_cb.new(action="delete")))
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


# Статистика опросов
async def statistics_pool(message: Message, state: FSMContext):
    owner_polls: list = await db_get_owner_polls(message.from_user.id)
    await state.update_data(page=0)
    await state.update_data(owner_polls=owner_polls)
    keyboard = await keyboard_statistics_poll(state)
    await message.answer("Ниже представлены ваши опросы.", reply_markup=keyboard)


async def next_statistics_poll(call: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    if (state_data['page'] + 1) * 3 < len(state_data['owner_polls']):
        await state.update_data(page=(state_data['page'] + 1))
    else:
        await state.update_data(page=0)
    keyboard = await keyboard_statistics_poll(state)
    await call.message.edit_text("Ниже представлены ваши опросы.", reply_markup=keyboard)


async def last_statistics_poll(call: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    if state_data['page'] * 3 > 0:
        await state.update_data(page=(state_data['page'] - 1))
    else:
        if len(state_data['owner_polls']) % 3 == 0:
            await state.update_data(page=(len(state_data['owner_polls']) // 3) - 1)
        else:
            await state.update_data(page=(len(state_data['owner_polls']) // 3))
    keyboard = await keyboard_statistics_poll(state)
    await call.message.edit_text("Ниже представлены ваши опросы.", reply_markup=keyboard)


async def keyboard_statistics_poll(state: FSMContext):
    state_data = await state.get_data()
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for i in range(0, 3):
        if state_data['page'] * 3 + i < len(state_data['owner_polls']):
            keyboard.add(KeyboardButton(text=state_data['owner_polls'][state_data['page'] * 3 + i].question,
                                        callback_data=statistics_answer_cb.new(id=i)))
    keyboard.add(KeyboardButton(text="<", callback_data=pool_cb.new(action="last")),
                 KeyboardButton(text=">", callback_data=pool_cb.new(action="next")))
    return keyboard


async def information_statistics_pool(call: CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    poll = state_data['owner_polls'][state_data['page'] * 3 + int(callback_data["id"])]
    dictionary = await db_get_statistics_pool(poll.id_poll)
    await call.bot.delete_message(call.message.chat.id, call.message.message_id)
    mes = "Ваш вопрос: " + str(poll.question) + "\n"
    for i in range(1, poll.count_answer):
        answ = 'answ_' + str(i)
        mes += "За ответ №" + str(i) + " проголосовало: " + str(dictionary.get(answ)) + " человек\n"
    await call.message.answer(mes)


# Блок закончен