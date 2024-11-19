from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from locales.locales import gettext
from logger.logger import logger


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
        user_locale = data.get('locale', None)
        if user_locale is None:
            user_locale = event.from_user.language_code \
                if isinstance(event, Message) or isinstance(event, CallbackQuery) \
                else 'en'
            data['locale'] = user_locale
            await data['state'].update_data({'locale': user_locale})

        data['_'] = gettext.get(user_locale, gettext['en'])
        return await handler(event, data)
