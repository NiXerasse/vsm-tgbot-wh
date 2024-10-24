from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from filters.is_admin import IsAdmin


async def authorised_start(message: Message, state: FSMContext, session, _):
    if await IsAdmin()(message, state):
        from handlers.admin import admin_start
        await admin_start(message, state, session, _)
    else:
        from handlers.employee import employee_cmd_start
        await employee_cmd_start(message, state, session, _)
