import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommandScopeAllPrivateChats
from dotenv import load_dotenv, find_dotenv

from common.bot_commands_list import bot_commands_list
from handlers.start import start_router

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

dp.include_routers(start_router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=bot_commands_list, scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit...')