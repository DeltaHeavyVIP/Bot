from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, KeyboardButton, \
    CallbackQuery
from aiogram.utils.callback_data import CallbackData

from app.db import db_get_owner_polls, db_get_statistics_pool
from app.handlers.create_pool import pool_cb

statistics_answer_cb = CallbackData("statistics_answer", "id")


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
