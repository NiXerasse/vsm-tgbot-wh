from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

start_router = Router()

@start_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(f'Привет!\nТвой ID: {message.from_user.id}\nИмя: {message.from_user.first_name}')

@start_router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Это команда /help')

@start_router.message(F.text == 'Как дела?')
async def how_are_you(message: Message):
    await message.answer('Да все в поряде!')
