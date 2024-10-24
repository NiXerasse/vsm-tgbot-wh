from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject

from logger.logger import logger


class IsAdmin(BaseFilter):
    async def __call__(self, obj: TelegramObject, state: FSMContext) -> bool:
        fsm_data = await state.get_data()
        logger.warning('is_admin')
        return fsm_data.get('is_admin', False)
