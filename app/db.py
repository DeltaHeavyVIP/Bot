from tortoise import Tortoise
from tortoise.backends.base.config_generator import generate_config
from tortoise.exceptions import IntegrityError

from app.model import Poll, Answer
from main import logger
from main import config


async def db_start():
    Url = f'{config.db_bot.db_type}://{config.db_bot.user}:{config.db_bot.password}@{config.db_bot.host}:{config.db_bot.port}/{config.db_bot.db_name}'
    tortoise_config: dict = generate_config(Url, {"models": ["app.model"]})
    await Tortoise.init(
        config=tortoise_config
    )
    await Tortoise.generate_schemas()


async def db_create_pool(id_owner: int, count_answer: int, question: str, answer_1: str, answer_2: str, answer_3: str,
                         answer_4: str,
                         answer_5: str, answer_6: str):
    await db_start()
    try:
        poll = await Poll.create(id_owner=id_owner, count_answer=count_answer, question=question, answer_1=answer_1,
                                 answer_2=answer_2, answer_3=answer_3,
                                 answer_4=answer_4, answer_5=answer_5, answer_6=answer_6)
        return poll
    except IntegrityError:
        logger.error("Данный опрос уже существует")
    finally:
        await db_close_connections()


async def db_create_answer(id_poll: int, id_respondent: int, number_answer: int):
    await db_start()
    try:
        await Answer.create(poll_id=id_poll, respondent=id_respondent, answer=number_answer)
    except IntegrityError:
        logger.error("А как какать?")
    finally:
        await db_close_connections()


async def db_is_respondent(id_poll: int, id_user: int):
    await db_start()
    ret = await Answer.filter(poll_id=id_poll, respondent=id_user).count()
    await db_close_connections()
    return ret


async def db_get_owner_polls(id_owner: int):
    await db_start()
    ret = await Poll.filter(id_owner=id_owner).all()
    await db_close_connections()
    return ret


async def db_get_statistics_pool(id_poll: int):
    dictionary = dict()
    await db_start()
    for i in range(1, 7):
        text = 'answ_' + str(i)
        dictionary[text] = await Answer.filter(poll=id_poll, answer=i).count()
    await db_close_connections()
    return dictionary


async def db_get_pool(id_poll: int):
    await db_start()
    poll = await Poll.filter(id_poll=id_poll).first()
    await db_close_connections()
    answers_poll = [poll.answer_1, poll.answer_2, poll.answer_3, poll.answer_4, poll.answer_5, poll.answer_6]
    return int(poll.count_answer), str(poll.question), answers_poll


async def db_close_connections():
    await Tortoise.close_connections()
