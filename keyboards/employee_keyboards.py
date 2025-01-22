from dataclasses import asdict

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callback_data.employee_callback_data import DetailedWhInfoCallback, ShowInquiryIdCallback, \
    AddMessageInquiryCallback, DeleteInquiryIdCallback, DoDeleteInquiryIdCallback, RateInfoCallback
from utils.util_data_types import MonthPeriod


class EmployeeKeyboards:
    @staticmethod
    def get_main_keyboard(has_answered_inquiries, _):
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text=_('Get worked hours info'), callback_data='get_wh_info'))
        inquiries_item = _('Inquiries')
        if has_answered_inquiries:
            inquiries_item += ' (*)'
        keyboard.add(InlineKeyboardButton(text=inquiries_item, callback_data='inquiry_menu'))
        keyboard.add(InlineKeyboardButton(text=_('Log out of your account'), callback_data='log_out_button'))
        return keyboard.adjust(1, 1).as_markup()

    @staticmethod
    def get_wh_main_info_keyboard(periods: [MonthPeriod], _):
        keyboard = InlineKeyboardBuilder()
        for period in periods:
            keyboard.add(InlineKeyboardButton(
                text=f'{period.month_str.capitalize()}\'{period.year % 100}',
                callback_data=DetailedWhInfoCallback(**asdict(period)).pack())
            )
        keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
        return keyboard.adjust(len(periods), 1).as_markup()

    @staticmethod
    def get_wh_info_keyboard(period: MonthPeriod, _):
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(
            text=_('Detailed'), callback_data=DetailedWhInfoCallback(**asdict(period)).pack()))
        keyboard.add(InlineKeyboardButton(text=_('The rate info'), callback_data=RateInfoCallback().pack()))
        keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
        return keyboard.adjust(1, 1, 1).as_markup()

    @staticmethod
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
            keyboard.add(
                InlineKeyboardButton(text=f'{i}', callback_data=ShowInquiryIdCallback(inquiry_id=inquiry.id).pack()))
        keyboard.add(InlineKeyboardButton(text=_('Write inquiry'), callback_data='write_inquiry'))
        keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
        return keyboard.adjust(*adj, 1, 1).as_markup()

    @staticmethod
    def get_send_back_button_keyboard(_):
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text=_('Send'), callback_data=f'send_button'))
        keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
        return keyboard.adjust(2).as_markup()

    @staticmethod
    def get_write_delete_back_button_keyboard(inquiry_id, _, add_message_menu=True):
        keyboard = InlineKeyboardBuilder()
        if add_message_menu:
            keyboard.add(InlineKeyboardButton(
                text=_('Add a message'), callback_data=AddMessageInquiryCallback(inquiry_id=inquiry_id).pack()))
        keyboard.add(InlineKeyboardButton(
            text=_('Delete the entire inquiry'), callback_data=DeleteInquiryIdCallback(inquiry_id=inquiry_id).pack()))
        keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
        return keyboard.adjust(1, 1, 1).as_markup()

    @staticmethod
    def get_delete_back_button_keyboard(inquiry_id, _):
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(
            text=_('Delete'), callback_data=DoDeleteInquiryIdCallback(inquiry_id=inquiry_id).pack()))
        keyboard.add(InlineKeyboardButton(text=_('Back'), callback_data='back_button'))
        return keyboard.adjust(2).as_markup()
