from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callback_data.auth_callback_data import ChooseLanguageCallback, PasswordOwnerCallback, SavePasswordCallback


class AuthKeyboards:
    @staticmethod
    def get_start_keyboard(_):
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text='Change language / Сменить язык', callback_data='change_language'))
        keyboard.add(InlineKeyboardButton(text=_('Login by PIN'), callback_data='login_pin'))
        keyboard.add(InlineKeyboardButton(text=_('Login by username'), callback_data='login_username'))
        return keyboard.adjust(1, 2).as_markup()

    @staticmethod
    def get_language_selection_keyboard(_):
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text='English', callback_data=ChooseLanguageCallback(locale='en').pack()))
        keyboard.add(InlineKeyboardButton(text='Русский', callback_data=ChooseLanguageCallback(locale='ru').pack()))
        return keyboard.adjust(2).as_markup()

    @staticmethod
    def get_got_it_back_button_keyboard(tab_no, _):
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text=_('Got it'), callback_data=PasswordOwnerCallback(tab_no=tab_no).pack()))
        keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
        return keyboard.adjust(2).as_markup()

    @staticmethod
    def get_save_back_button_keyboard(password, _):
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text=_('Save'), callback_data=SavePasswordCallback(password=password).pack()))
        keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
        return keyboard.adjust(2).as_markup()

    @staticmethod
    def get_change_login_back_button_keyboard(_):
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text=_('Change username'), callback_data='change_login'))
        keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
        return keyboard.adjust(2).as_markup()
