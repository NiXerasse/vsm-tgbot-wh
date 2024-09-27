import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(f'Привет!\nТвой ID: {message.from_user.id}\nИмя: {message.from_user.first_name}')

@dp.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Это команда /help')

@dp.message(F.text == 'Как дела?')
async def how_are_you(message: Message):
    await message.answer('Да все в поряде!')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit...')