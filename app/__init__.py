from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from .handlers import *


def register_handlers_start(dp: Dispatcher):
    dp.register_message_handler(finish_answer, commands="finish", state="*")
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
    dp.register_callback_query_handler(information_statistics_pool, Text(startswith="statistics_answer_"), state="*")
