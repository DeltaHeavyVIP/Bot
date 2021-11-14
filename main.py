import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app import register_handlers_start
from app.db import db_start, db_close_connections
from app.read_conf import load_config


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Описание бота"),
        BotCommand(command="/finish", description="Коммунистические ответы закончились")
    ]
    await bot.set_my_commands(commands)


async def main():
    config = load_config("config/bot.ini")
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher(bot, storage=MemoryStorage())

    await db_start(config)

    register_handlers_start(dp)

    await set_commands(bot)

    await dp.start_polling()

    await db_close_connections()


if __name__ == '__main__':
    asyncio.run(main())
