from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker

from database.orm import add_user


class DataBaseSession(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool


    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data['session'] = session

            bot_id = data['bot'].id
            user_id, chat_id = None, None
            if isinstance(event, Message):
                user_id = event.from_user.id
                chat_id = event.chat.id
            elif isinstance(event, CallbackQuery):
                user_id = event.from_user.id
                chat_id = event.message.chat.id

            if bot_id and user_id and chat_id:
                await add_user(session, bot_id, user_id, chat_id)

            return await handler(event, data)