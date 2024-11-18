from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.auth_service.auth_service import AuthService


class AuthBaseHandlers:
    router = Router()
    auth_service = AuthService()

    @staticmethod
    @router.message(Command('get_my_id'))
    async def get_my_id(message: Message, _):
        await message.answer(f'Test {_('Hello')}')
