import asyncio
import logging
import app.handlers as h

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.read_conf import load_config

logger = logging.getLogger(__name__)
config = load_config("config/bot.ini")


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Описание бота"),
        BotCommand(command="/finish", description="Коммунистические ответы закончились")
    ]
    await bot.set_my_commands(commands)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(bot, storage=MemoryStorage())

    h.register_handlers_start(dp)

    await set_commands(bot)

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
