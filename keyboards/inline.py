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
    keyboard.add(InlineKeyboardButton(text=_('Inquiries'), callback_data='inquiry_menu'))
    keyboard.add(InlineKeyboardButton(text=_('Log out of your account'), callback_data='log_out_button'))
    return keyboard.adjust(1, 1).as_markup()

def get_wh_info_keyboard(_):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
    return keyboard.adjust(1).as_markup()

def get_inquiry_menu_keyboard(inquiries, _):
    keyboard = InlineKeyboardBuilder()
    inquiries_cnt = len(inquiries)
    inq_on_one_line = 4
    adj = []
    if inquiries_cnt:
        adj = [inq_on_one_line] * (inquiries_cnt // inq_on_one_line)
        if inquiries_cnt % inq_on_one_line:
            adj.append(inquiries_cnt % inq_on_one_line)
    for i, inquiry in enumerate(inquiries, start=1):
        keyboard.add(InlineKeyboardButton(text=f'{i}', callback_data=f'inquiry_menu_{inquiry.id}'))
    keyboard.add(InlineKeyboardButton(text=_('Write inquiry'), callback_data='write_inquiry'))
    keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
    return keyboard.adjust(*adj, 1, 1).as_markup()

def get_send_back_button_keyboard(_):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('Send'), callback_data=f'send_button'))
    keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
    return keyboard.adjust(2).as_markup()

def get_write_delete_back_button_keyboard(inquiry_id, _):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('Add a message'), callback_data=f'add_message_{inquiry_id}'))
    keyboard.add(InlineKeyboardButton(text=_('Delete the entire inquiry'), callback_data=f'delete_inquiry_{inquiry_id}'))
    keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
    return keyboard.adjust(1, 1, 1).as_markup()

def get_delete_back_button_keyboard(inquiry_id, _):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('Delete'), callback_data=f'delete_inquiry_{inquiry_id}'))
    keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
    return keyboard.adjust(2).as_markup()

def get_inquiry_answer_keyboard(inquiry_id, _):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=_('Send to bot for answer'), callback_data=f'answer_{inquiry_id}'))
    keyboard.add(InlineKeyboardButton(text=_('Go to bot'), url='https://t.me/vsminfo_dev_bot'))
    return keyboard.adjust(2).as_markup()
