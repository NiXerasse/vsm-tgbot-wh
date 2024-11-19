from aiogram import F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import Message, InlineKeyboardMarkup

from callback_data.auth_callback_data import PasswordOwnerCallback, SavePasswordCallback
from keyboards.auth_keyboards import AuthKeyboards
from keyboards.common_keyboards import CommonKeyboards
from .auth_base_handlers import AuthBaseHandlers
from fsm.fsm_states.fsm_states import Unauthorised
from services.auth_service.auth_result import AuthResult
from services.auth_service.auth_status import AuthStatus
from utils.message_builders.auth_message_builder import AuthMessageBuilder
from utils.message_manager import MessageManager


class AuthPinHandlers(AuthBaseHandlers):
    @staticmethod
    @AuthBaseHandlers.router.callback_query(StateFilter(Unauthorised.start_menu), (F.data == 'login_pin'))
    async def enter_pin_button_pressed(callback: types.CallbackQuery, state: FSMContext, _):
        await MessageManager.update_message(
            callback.message, AuthMessageBuilder.enter_pin_message(_), CommonKeyboards.get_back_button_keyboard(_))
        await state.set_state(Unauthorised.entering_pin)

    @staticmethod
    @AuthBaseHandlers.router.message(Unauthorised.entering_pin)
    async def process_pin(message: Message, state: FSMContext, session, _, start_msg_id=None):
        pin = message.text.upper()

        result = await AuthPinHandlers.auth_service.authorize_employee_by_pin(session, pin)
        new_message, new_state, new_keyboard = AuthPinHandlers._build_auth_pin_response(result, _)

        await MessageManager.update_main_message(message, state, start_msg_id, new_message, new_keyboard)
        await state.set_state(new_state)

    @staticmethod
    def _build_auth_pin_response(result: AuthResult, _) -> tuple[str, State, InlineKeyboardMarkup]:
        response_map = {
            AuthStatus.NOT_FOUND: lambda: (
                AuthMessageBuilder.pin_error_message(_),
                Unauthorised.start_menu,
                AuthKeyboards.get_start_keyboard(_)
            ),
            AuthStatus.ALREADY_AUTHORIZED: lambda: (
                AuthMessageBuilder.already_authorized_message(_),
                Unauthorised.start_menu,
                AuthKeyboards.get_start_keyboard(_)
            ),
            AuthStatus.SUCCESS: lambda: (
                AuthMessageBuilder.authorization_success_message(result.employee, _),
                Unauthorised.correct_pin_entered,
                AuthKeyboards.get_got_it_back_button_keyboard(result.employee.tab_no, _)
            )
        }

        return response_map[result.status]()

    @staticmethod
    @AuthBaseHandlers.router.callback_query(
        StateFilter(Unauthorised.correct_pin_entered), PasswordOwnerCallback.filter())
    async def enter_new_password(
            callback: types.CallbackQuery, state: FSMContext, callback_data: PasswordOwnerCallback, _):
        tab_no = callback_data.tab_no
        # tab_no_msg = await callback.message.answer(text=tab_no)
        # await state.update_data({'tab_no_msg_id': tab_no_msg.message_id, 'tab_no': tab_no})
        await state.update_data({'tab_no_msg_id': None, 'tab_no': tab_no})

        await MessageManager.update_message(
            callback.message, AuthMessageBuilder.edit_password_message(_), CommonKeyboards.get_back_button_keyboard(_))
        await state.set_state(Unauthorised.entering_new_password)

    @staticmethod
    @AuthBaseHandlers.router.message(Unauthorised.entering_new_password)
    async def process_new_password(message: Message, state: FSMContext, _, tab_no, start_msg_id=None):
        password = message.text
        await MessageManager.update_main_message(
            message, state, start_msg_id, AuthMessageBuilder.save_password_message(tab_no, password, _),
            AuthKeyboards.get_save_back_button_keyboard(password, _))
        await state.set_state(Unauthorised.new_password_entered)

    @staticmethod
    @AuthBaseHandlers.router.callback_query(
        StateFilter(Unauthorised.new_password_entered), SavePasswordCallback.filter())
    async def save_account_data(
            callback: types.CallbackQuery, state: FSMContext, session, callback_data: SavePasswordCallback, _, tab_no):
        await AuthPinHandlers.auth_service.set_employee_password(session, tab_no, callback_data.password)
        await MessageManager.update_message(
            callback.message, AuthMessageBuilder.account_saved_message(_), AuthKeyboards.get_start_keyboard(_))
        await state.set_state(Unauthorised.start_menu)
