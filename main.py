import asyncio
import betterlogging as logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from core import settings
from core.handlers.basic import get_start, get_location, get_description, get_photo
from core.handlers.callback import catch_event, type_event, choose_event, deletion_callback
from core.utils.states import Steps
from core.settings import settings
from core.utils.commands import set_commands
from core.middlewares.dbmiddleware import DbSession
from core.utils.dbconnect import Request
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from map import update
import psycopg_pool


async def start_bot(bot: Bot):
    await set_commands(bot)
    await bot.send_message(settings.bots.admin_id, text='Бот запущен!')


async def stop_bot(bot: Bot):
    await bot.send_message(settings.bots.admin_id, text="Бот остановлен!")


def create_pool():
    return psycopg_pool.AsyncConnectionPool(f" host = {settings.bots.host } "
                                            f" port = {5432} "
                                            f" dbname = {settings.bots.database } "
                                            f" user = {settings.bots.user } "
                                            f" password = {settings.bots.password }"
                                            f" connect_timeout = 60 ")


async def start():
    logging.basic_colorized_config(level=logging.INFO,
                                   format="%(asctime)s - [%(levelname)s] - %(name)s - "
                                          "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
                                   )
    bot = Bot(token=settings.bots.bot_token, parse_mode="HTML")
    pool_connect = create_pool()
    request = Request(pool_connect)
    dp = Dispatcher()
    dp.update.middleware.register(DbSession(pool_connect))
    scheduler = AsyncIOScheduler(timezone="Europe/Kiev")
    scheduler.add_job(update, 'interval', minutes=1, args=(bot, request))
    scheduler.start()
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    dp.callback_query.register(deletion_callback, Steps.DROP_EVENT)
    dp.callback_query.register(choose_event, Steps.EDIT_EVENT)
    dp.callback_query.register(type_event, Steps.TYPE_EVENT)
    dp.message.register(get_description, F.text, Steps.DESCRIPTION)
    dp.message.register(get_photo, F.photo, Steps.DESCRIPTION)
    dp.message.register(get_location, F.location or F.text == '🚫 недопустимые координаты', Steps.LOCATION)
    dp.callback_query.register(catch_event)
    dp.message.register(get_start, Command(commands='start'))

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await pool_connect.close()  # Close the connection pool


if __name__ == "__main__":
    asyncio.run(start())
