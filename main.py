import asyncio
import os

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from config.env import google_credentials_file, read_file_postfix, admin_group_id

from services.gsheets_service.gsheets_service import GoogleSheetsService
from database.db_sync_coordinator import DatabaseSyncCoordinator
from services.admin_group_message_updater_service.admin_group_message_updater_service import \
    AdminGroupMessageUpdaterService

from aiogram import Bot, Dispatcher
from middlewares.fsm_data_middleware import FSMDataMiddleware
from middlewares.i18n_middleware import I18nMiddleware
from middlewares.session_middleware import DataBaseSession

from database.engine import create_db, session_maker
from fsm.fsm_storage import PostgresFSMStorage

from handlers.auth_handlers.auth_base_handlers import AuthBaseHandlers
from handlers.employee_handlers.employee_base_handlers import EmployeeBaseHandlers
from handlers.admin_handlers.admin_base_handlers import AdminBaseHandlers
from handlers.admin_group_handlers.admin_group_service_handlers import AdminGroupServiceHandlers

bot = Bot(token=os.getenv('BOT_TOKEN'))
storage = PostgresFSMStorage(session_maker)
dp = Dispatcher(storage=storage)

dp.include_routers(
    AdminBaseHandlers.router,
    AdminGroupServiceHandlers.router,
    EmployeeBaseHandlers.router,
    AuthBaseHandlers.router,
)

async def on_startup():
    ...

async def on_shutdown():
    print('Shutting down...')

async def main():
    await create_db()

    asyncio.create_task(
        DatabaseSyncCoordinator(
            session_maker,
            GoogleSheetsService(google_credentials_file, read_file_postfix)
        ).update_all_loop(interval=60)
    )

    asyncio.create_task(
        AdminGroupMessageUpdaterService(session_maker, bot, admin_group_id).update_admin_group_messages_loop(
            interval=3600,
            hours_older_than=44
        )
    )

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    dp.update.middleware(FSMDataMiddleware())
    dp.update.middleware(I18nMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit...')
