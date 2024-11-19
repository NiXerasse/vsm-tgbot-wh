from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callback_data.admin_group_inquiry_callback_data import InquiryAnswerCallback
from datetime import datetime as dt

from config.env import bot_http_link


class AdminGroupInquiryKeyboards:
    @staticmethod
    def get_inquiry_answer_keyboard(inquiry_id, _):
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text=_('Send to bot for answer'),
                                          callback_data=InquiryAnswerCallback(
                                              inquiry_id=inquiry_id,
                                              post_time=dt.now()
                                          ).pack()))
        keyboard.add(InlineKeyboardButton(text=_('Go to bot'), url=bot_http_link))
        return keyboard.adjust(2).as_markup()
