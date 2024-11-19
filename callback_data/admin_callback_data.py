from aiogram.filters.callback_data import CallbackData

class ResetPasswordCallback(CallbackData, prefix='reset_password'):
    ...

class ResetPasswordCallbackData(CallbackData, prefix='reset_password'):
    employee_id: int
