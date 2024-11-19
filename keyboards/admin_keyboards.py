from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callback_data.admin_callback_data import ResetPasswordCallback, ResetPasswordCallbackData
from config.env import admin_group_id


class AdminKeyboards:
    @staticmethod
    async def get_main_admin_keyboard(bot, _):
        keyboard = InlineKeyboardBuilder()
        admin_group_invite_link = (await bot.get_chat(admin_group_id)).invite_link
        keyboard.add(InlineKeyboardButton(text=_('Inquiries'), url=admin_group_invite_link))
        keyboard.add(InlineKeyboardButton(
            text=_('Reset employee password'), callback_data=ResetPasswordCallback().pack()))
        keyboard.add(InlineKeyboardButton(text=_('Log out of your account'), callback_data='log_out_button'))
        return keyboard.adjust(1, 1).as_markup()

    @staticmethod
    def get_reset_password_back_keyboard(employee_id, _):
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(
            text=_('Reset password'), callback_data=ResetPasswordCallbackData(employee_id=employee_id).pack())
        )
        keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
        return keyboard.adjust(2,).as_markup()
