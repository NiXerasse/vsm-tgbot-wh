import asyncio

from aiogram import Bot, Dispatcher

from config.env import bot_token, webhook_enabled
from core.middleware_manager import MiddlewareManager
from core.router_manager import RouterManager
from core.task_manager import TaskManager
from core.webhook_manager import WebhookManager
from database.engine import session_maker, create_db
from fsm.fsm_storage import PostgresFSMStorage


class BotApplication:
    def __init__(self):
        self.bot = Bot(token=bot_token)
        self.storage = PostgresFSMStorage(session_maker)
        self.dispatcher = Dispatcher(storage=self.storage)

        self.router_manager = RouterManager(self.dispatcher)
        self.middleware_manager = MiddlewareManager(self.dispatcher, session_maker)
        self.task_manager = TaskManager(session_maker, self.bot)
        self.webhook_manager = WebhookManager(self.dispatcher, self.bot)

    async def startup(self):
        await create_db()
        self.router_manager.setup()
        self.middleware_manager.setup()
        await self.task_manager.start_tasks()

    async def run(self):
        await self.startup()

        if webhook_enabled:
            await self.webhook_manager.start_webhook()

            try:
                while True:
                    await asyncio.sleep(3600)  # Keep running
            except KeyboardInterrupt:
                print("Webhook server stopped.")
                await self.webhook_manager.stop_webhook()
        else:
            await self.bot.delete_webhook(drop_pending_updates=True)
            await self.dispatcher.start_polling(self.bot)
