from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from locales.locales import gettext

class I18nMiddleware(BaseMiddleware):
    def __init__(self, default='en'):
        super(I18nMiddleware, self).__init__()
        self.default_language = default

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        state = data['state']
        preferred_user_language = None
        if isinstance(event, Message) or isinstance(event, CallbackQuery):
            preferred_user_language = event.from_user.language_code
        user_locale = (await state.get_data()).get('locale') or preferred_user_language
        data['_'] = gettext.get(user_locale, gettext['en'])
        return await handler(event, data)