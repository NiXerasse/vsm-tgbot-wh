from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class MenuCallBack(CallbackData, prefix='btn'):
    stage: str

def get_start_keyboard(_):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Change language / Сменить язык', callback_data='change_language'))
    keyboard.add(InlineKeyboardButton(text=_('Login by PIN'), callback_data='login_pin'))
    keyboard.add(InlineKeyboardButton(text=_('Login by username'), callback_data='login_username'))
    return keyboard.adjust(1, 2).as_markup()

def get_language_selection_keyboard(_):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='English', callback_data='change_language_en'))
    keyboard.add(InlineKeyboardButton(text='Русский', callback_data='change_language_ru'))
    return keyboard.adjust(2).as_markup()

def get_back_button_keyboard(_):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
    return keyboard.adjust(1).as_markup()

def get_got_it_back_button_keyboard(callback_data, _):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('Got it'), callback_data=f'got_it_button_{callback_data}'))
    keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
    return keyboard.adjust(2).as_markup()

def get_save_back_button_keyboard(callback_data, _):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('Save'), callback_data=f'save_button_{callback_data}'))
    keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
    return keyboard.adjust(2).as_markup()

def get_change_login_back_button_keyboard(_):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('Change username'), callback_data='change_login'))
    keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
    return keyboard.adjust(2).as_markup()

def get_main_keyboard(_):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('Get worked hours info'), callback_data='get_wh_info'))
    keyboard.add(InlineKeyboardButton(text=_('Log out of your account'), callback_data='log_out_button'))
    return keyboard.adjust(1, 1).as_markup()

def get_wh_info_keyboard(_):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
    return keyboard.adjust(1).as_markup()
