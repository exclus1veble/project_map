from dataclasses import dataclass
from environs import Env


@dataclass()
class Bots:
    bot_token: str
    admin_id: int
    channel_id: int
    database: str
    user: str
    password: str
    host: str
    port: int


@dataclass()
class Settings:
    bots: Bots


def get_settings(path: str):
    env = Env()
    env.read_env(path)

    return Settings(
        bots=Bots(
            bot_token=env.str("BOT_TOKEN"),
            admin_id=env.str("ADMIN_ID"),
            channel_id=env.str("CHANNEL_ID"),
            database=env.str("DATABASE"),
            user=env.str("USER"),
            password=env.str("PASSWORD"),
            host=env.str("HOST"),
            port=env.str("PORT")
        )
    )


settings = get_settings('input')
