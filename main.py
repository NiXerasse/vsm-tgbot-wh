import asyncio
import os

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


from aiogram import Bot, Dispatcher
from middlewares.i18n import I18nMiddleware
from middlewares.session import DataBaseSession


from database.engine import create_db, session_maker
from database.fsm_storage import PostgresFSMStorage
from database.db_gsheets_updater import sync_db_and_gsheets_loop

from handlers.start import start_router
from handlers.admin_group import admin_group_router

bot = Bot(token=os.getenv('BOT_TOKEN'))
storage = PostgresFSMStorage(session_maker)
dp = Dispatcher(storage=storage)

dp.include_routers(start_router, admin_group_router)

async def on_startup():
    ...

async def on_shutdown():
    print('Shutting down...')

async def main():
    await create_db()

    asyncio.create_task(sync_db_and_gsheets_loop(60))

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    dp.update.middleware(I18nMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit...')