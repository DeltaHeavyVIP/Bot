import configparser
from dataclasses import dataclass
from dacite import from_dict


@dataclass
class TgBot:
    token: str
    admin_id: str


@dataclass
class DbBot:
    db_type: str
    db_name: str
    user: str
    password: str
    host: str
    port: str


@dataclass
class Config:
    tg_bot: TgBot
    db_bot: DbBot


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path)

    tg_bot = config._sections["tg_bot"]
    tg_bot = from_dict(data_class=TgBot, data=tg_bot)

    db_bot = config._sections["db_bot"]
    db_bot = from_dict(data_class=DbBot, data=db_bot)

    return Config(
        tg_bot,
        db_bot
    )
