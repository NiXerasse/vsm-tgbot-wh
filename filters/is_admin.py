from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject

from logger.logger import logger


class IsAdmin(BaseFilter):
    async def __call__(self, obj: TelegramObject, user_state: FSMContext) -> bool:
        fsm_data = await user_state.get_data()
        logger.warning(f'is_admin: {fsm_data.get('is_admin', False)}\nfsm_data: {fsm_data}')
        return fsm_data.get('is_admin', False)