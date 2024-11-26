from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callback_data.admin_group_service_callback_data import RegisterThreadCallback
from config.env import group_command_postfix


class AdminGroupServiceKeyboards:
    @staticmethod
    def get_subdivision_thread_register_keyboard(subdivisions, message_thread_id):
        keyboard = InlineKeyboardBuilder()
        for subdivision in subdivisions:
            keyboard.add(InlineKeyboardButton(
                text=subdivision.name,
                callback_data=RegisterThreadCallback(
                    group_command_postfix=group_command_postfix,
                    subdivision_id=subdivision.id,
                    message_thread_id=message_thread_id or 0
                ).pack())
            )
        return keyboard.adjust(1).as_markup()
