import configparser
from dataclasses import dataclass


@dataclass
class TgBot:
    token: str
    admin_id: int


@dataclass
class DbBot:
    db_type: str
    db_name: str
    user: str
    password: str
    host: str
    port: int


@dataclass
class Config:
    tg_bot: TgBot
    db_bot: DbBot


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path)

    tg_bot = config["tg_bot"]
    db_bot = config["db_bot"]

    return Config(
        tg_bot=TgBot(
            token=tg_bot["token"],
            admin_id=int(tg_bot["admin_id"])
        ),
        db_bot=DbBot(
            db_type=db_bot["db_type"],
            db_name=db_bot["db_name"],
            user=db_bot["user"],
            password=db_bot["password"],
            host=db_bot["host"],
            port=int(db_bot["port"])
        )
    )
