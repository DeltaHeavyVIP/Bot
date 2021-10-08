from tortoise import Tortoise
from tortoise.backends.base.config_generator import generate_config
from tortoise.exceptions import IntegrityError

from app.model import Poll, Answer
from app.read_conf import Config
from main import logger


async def db_start(config: Config):
    Url = f'{config.db_bot.db_type}://{config.db_bot.user}:{config.db_bot.password}@{config.db_bot.host}:{config.db_bot.port}/{config.db_bot.db_name}'
    tortoise_config: dict = generate_config(Url, {"models": ["app.dbModel"]})
    await Tortoise.init(
        config=tortoise_config
    )
    await Tortoise.generate_schemas()


async def db_create_pool(id_owner: int, question: str, answer_1: str, answer_2: str, answer_3: str, answer_4: str,
                         answer_5: str, answer_6: str):
    try:
        await Poll.create(id_owner=id_owner, question=question, answer_1=answer_1, answer_2=answer_2, answer_3=answer_3,
                          answer_4=answer_4, answer_5=answer_5, answer_6=answer_6)
    except IntegrityError:
        logger.error("Данный опрос уже существует")


async def db_create_answer(id_poll: int, id_respondent: int, number_answer: int):
    try:
        await Answer.create(id_poll=id_poll, id_respondent=id_respondent, number_answer=number_answer)
    except IntegrityError:
        logger.error("А как какать?")


async def is_respondent(id_poll: int, id_owner: int):
    await Answer.filter(id_poll=id_poll, id_owner=id_owner).first()


async def db_close_connections():
    await Tortoise.close_connections()
