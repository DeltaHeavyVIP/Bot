from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from app.handlers.start import *
from app.handlers.create_pool import *
from app.handlers.statistics_pool import *


def register_handlers_start(dp: Dispatcher):
    dp.register_message_handler(finish_answer, commands="finish", state="*")
    dp.register_callback_query_handler(resume_pool, pool_cb.filter(action='resume'),
                                       state=OrderAnswer.waiting_for_answer)
    dp.register_callback_query_handler(delete_pool, pool_cb.filter(action='delete'),
                                       state=OrderAnswer.waiting_for_answer)

    dp.register_message_handler(start, commands="start", state="*")
    dp.register_message_handler(create_pool, Text(equals="Создать опрос", ignore_case=True), state="*")
    dp.register_message_handler(wait_question, state=OrderAnswer.waiting_for_question)
    dp.register_message_handler(wait_answer, state=OrderAnswer.waiting_for_answer)
    dp.register_callback_query_handler(call_back_answer, answer_cb.filter(), state="*")

    dp.register_message_handler(statistics_pool, Text(equals="Статистика опросов", ignore_case=True), state="*")
    dp.register_callback_query_handler(next_statistics_poll, pool_cb.filter(action='next'), state="*")
    dp.register_callback_query_handler(last_statistics_poll, pool_cb.filter(action='last'), state="*")
    dp.register_callback_query_handler(information_statistics_pool, statistics_answer_cb.filter(), state="*")
