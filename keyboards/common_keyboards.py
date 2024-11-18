from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class CommonKeyboards:
    @staticmethod
    def get_back_button_keyboard(_):
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
        return keyboard.adjust(1).as_markup()
