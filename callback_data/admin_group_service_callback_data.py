from aiogram.filters.callback_data import CallbackData

from config.env import group_command_postfix


class RegisterThreadCallback(CallbackData, prefix=f'register_thread{group_command_postfix}'):
    subdivision_id: int
    message_thread_id: int
