from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, obj: Union[Message, CallbackQuery]) -> bool:
        chat = None
        if isinstance(obj, Message):
            chat = obj.chat
        elif isinstance(obj, CallbackQuery) and obj.message:
            chat = obj.message.chat

        if chat:
            if isinstance(self.chat_type, str):
                return chat.type == self.chat_type
            else:
                return chat.type in self.chat_type
        return False
