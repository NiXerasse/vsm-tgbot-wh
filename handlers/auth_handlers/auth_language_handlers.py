from aiogram import types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from callback_data.auth_callback_data import ChooseLanguageCallback
from keyboards.auth_keyboards import AuthKeyboards
from .auth_base_handlers import AuthBaseHandlers
from fsm.fsm_states.fsm_states import Unauthorised
from locales.locales import gettext
from utils.message_builders.auth_message_builder import AuthMessageBuilder
from utils.message_manager import MessageManager


class AuthLanguageHandlers(AuthBaseHandlers):
    @staticmethod
    @AuthBaseHandlers.router.callback_query(StateFilter(Unauthorised.start_menu), (F.data == 'change_language'))
    async def change_language_button_pressed(callback: types.CallbackQuery, state: FSMContext, _):
        await MessageManager.update_message(
            callback.message, AuthMessageBuilder.choose_language_message(_),
            AuthKeyboards.get_language_selection_keyboard(_))
        await state.set_state(Unauthorised.choosing_language)

    @staticmethod
    @AuthBaseHandlers.router.callback_query(StateFilter(Unauthorised.choosing_language), ChooseLanguageCallback.filter())
    async def specific_language_button_pressed(
            callback: types.CallbackQuery, state: FSMContext, callback_data: ChooseLanguageCallback):
        language = callback_data.locale
        await MessageManager.update_message(
            callback.message, '', AuthKeyboards.get_start_keyboard(gettext[language]))
        await state.update_data({'locale': language})
        await state.set_state(Unauthorised.start_menu)
