from aiogram.filters.callback_data import CallbackData


class ChooseLanguageCallback(CallbackData, prefix='language'):
    locale: str

class PasswordOwnerCallback(CallbackData, prefix='password_owner_info'):
    tab_no: str

class SavePasswordCallback(CallbackData, prefix='save_password'):
    password: str
