from pprint import pprint
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import TelegramObject, Message, CallbackQuery
from sqlalchemy.ext.asyncio import async_sessionmaker

from database.orm import add_user
from logger.logger import logger


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
            logger.warning(f'{pprint(event)}')

            data['session'] = session

            bot_id = data['bot'].id
            user_id, chat_id = None, None
            if event.message:
                user_id = event.message.from_user.id
                chat_id = event.message.chat.id
            elif event.callback_query:
                user_id = event.callback_query.from_user.id
                chat_id = event.callback_query.message.chat.id

            if bot_id and user_id and chat_id:
                await add_user(session, bot_id, user_id, chat_id)

                if chat_id > 0:
                    data['user_state'] = data['state']
                else:
                    data['user_state'] = FSMContext(
                        storage=data['state'].storage,
                        key=StorageKey(
                        bot_id=data['bot'].id,
                        user_id=user_id,
                        chat_id=user_id
                        )
                    )

            return await handler(event, data)
