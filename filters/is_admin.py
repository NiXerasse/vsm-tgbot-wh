from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject


class IsAdmin(BaseFilter):
    async def __call__(self, obj: TelegramObject, is_admin=False) -> bool:
        return is_admin
