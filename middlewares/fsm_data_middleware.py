from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class FSMDataMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        fsm_context = data.get('state')
        if fsm_context:
            fsm_data = await fsm_context.get_data()
            data.update(fsm_data)
        return await handler(event, data)
