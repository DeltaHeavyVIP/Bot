from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, KeyboardButton, \
    CallbackQuery
from aiogram.utils.callback_data import CallbackData

from app.db import db_get_owner_polls, db_get_statistics_pool
from app.handlers.create_pool import pool_cb

statistics_answer_cb = CallbackData("statistics_answer", "id")
k = 3


# Статистика опросов
async def statistics_pool(message: Message, state: FSMContext):
    owner_polls: list = await db_get_owner_polls(message.from_user.id)
    await state.update_data(page=0)
    await state.update_data(owner_polls=owner_polls)
    keyboard = await keyboard_statistics_poll(state)
    await message.answer("Ниже представлены ваши опросы.", reply_markup=keyboard)


async def next_statistics_poll(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_proxy:
        if (state_proxy['page'] + 1) * k < len(state_proxy['owner_polls']):
            state_proxy['page'] += 1
        else:
            state_proxy['page'] = 0
    keyboard = await keyboard_statistics_poll(state)
    await call.message.edit_text("Ниже представлены ваши опросы.", reply_markup=keyboard)


async def last_statistics_poll(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as state_proxy:
        if state_proxy['page'] > 0:
            state_proxy['page'] -= 1
        else:
            if len(state_proxy['owner_polls']) % k == 0:
                state_proxy['page'] = (len(state_proxy['owner_polls']) // k) - 1
            else:
                state_proxy['page'] = (len(state_proxy['owner_polls']) // k)
    keyboard = await keyboard_statistics_poll(state)
    await call.message.edit_text("Ниже представлены ваши опросы.", reply_markup=keyboard)


async def keyboard_statistics_poll(state: FSMContext):
    state_data = await state.get_data()
    keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for i in range(0, k):
        if state_data['page'] * k + i < len(state_data['owner_polls']):
            keyboard.add(KeyboardButton(text=state_data['owner_polls'][state_data['page'] * k + i].question,
                                        callback_data=statistics_answer_cb.new(id=i)))
    if len(state_data['owner_polls']) > k:
        keyboard.add(KeyboardButton(text="<", callback_data=pool_cb.new(action="last")),
                     KeyboardButton(text=">", callback_data=pool_cb.new(action="next")))
    return keyboard


async def information_statistics_pool(call: CallbackQuery, callback_data: dict, state: FSMContext):
    state_data = await state.get_data()
    poll = state_data['owner_polls'][state_data['page'] * k + int(callback_data["id"])]
    dictionary = await db_get_statistics_pool(poll.id_poll)
    await call.bot.delete_message(call.message.chat.id, call.message.message_id)
    mes = "Ваш вопрос: " + str(poll.question) + "\n"
    for i in range(1, poll.count_answer + 1):
        answ = 'answ_' + str(i)
        mes += "За ответ №" + str(i) + " проголосовало: " + str(dictionary.get(answ)) + " человек\n"
    await call.message.answer(mes)

# Блок закончен
