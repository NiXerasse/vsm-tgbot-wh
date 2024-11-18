from datetime import datetime

from aiogram.filters.callback_data import CallbackData

from config.env import group_command_postfix


class InquiryAnswerCallback(CallbackData, prefix=f'answer_inquiry{group_command_postfix}', sep='#'):
    inquiry_id: int
    post_time: datetime
