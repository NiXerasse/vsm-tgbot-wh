from aiogram import F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.auth_keyboards import AuthKeyboards
from keyboards.common_keyboards import CommonKeyboards
from services.employee_service.employee_service import EmployeeService
from .auth_base_handlers import AuthBaseHandlers
from database.models import Employee
from fsm.fsm_states.fsm_states import Unauthorised
from utils.message_builders.auth_message_builder import AuthMessageBuilder
from utils.message_manager import MessageManager
from .auth_nav_handlers import AuthNavHandlers


class AuthLoginHandlers(AuthBaseHandlers):
    @staticmethod
    @AuthBaseHandlers.router.callback_query(StateFilter(Unauthorised.entering_password), (F.data == 'change_login'))
    async def change_login(callback: types.CallbackQuery, state: FSMContext, _):
        await MessageManager.update_message(
            callback.message, AuthMessageBuilder.enter_login_message(_), CommonKeyboards.get_back_button_keyboard(_))
        await state.set_state(Unauthorised.entering_login)

    @staticmethod
    @AuthBaseHandlers.router.callback_query(StateFilter(Unauthorised.start_menu), (F.data == 'login_username'))
    async def login_by_username(callback: types.CallbackQuery, state: FSMContext, session, _, tab_no=None):
        if tab_no is None:
            await AuthLoginHandlers._prompt_for_tab_no(callback, state, _)
            return

        employee = await AuthLoginHandlers.auth_service.get_employee_by_tab_no(session, tab_no)
        await AuthLoginHandlers._prompt_for_password(callback, state, employee, _)

    @staticmethod
    async def _prompt_for_tab_no(callback: types.CallbackQuery, state: FSMContext, _):
        await MessageManager.update_message(
            callback.message, AuthMessageBuilder.enter_login_message(_), CommonKeyboards.get_back_button_keyboard(_))
        await state.set_state(Unauthorised.entering_login)

    @staticmethod
    async def _prompt_for_password(
            callback: types.CallbackQuery, state: FSMContext, employee: Employee, _):
        await MessageManager.update_message(
            callback.message, AuthMessageBuilder.enter_password_message(employee, _),
            AuthKeyboards.get_change_login_back_button_keyboard(_))
        await state.update_data({'login_tab_no': employee.tab_no})
        await state.set_state(Unauthorised.entering_password)

    @staticmethod
    @AuthBaseHandlers.router.message(Unauthorised.entering_login)
    async def process_login(message: Message, state: FSMContext, session, _, start_msg_id=None):
        tab_no = EmployeeService.format_tab_no(message.text)
        employee = await AuthLoginHandlers._get_employee_by_tab_no_or_handle_error(
            message, state, session, tab_no, _, start_msg_id)

        if employee is None:
            return

        await AuthLoginHandlers._prompt_for_password_for_tab_no(message, state, tab_no, _, start_msg_id)

    @staticmethod
    async def _get_employee_by_tab_no_or_handle_error(
            message: Message, state: FSMContext, session, tab_no: str, _, start_msg_id: int | None) -> Employee | None:
        employee = await AuthLoginHandlers.auth_service.get_employee_by_tab_no(session, tab_no)
        if employee is None:
            await MessageManager.update_main_message(
                message, state, start_msg_id,
                AuthMessageBuilder.err_wrong_tab_no_message(_), CommonKeyboards.get_back_button_keyboard(_))
            await state.set_state(Unauthorised.entering_login)
        return employee

    @staticmethod
    async def _prompt_for_password_for_tab_no(
            message: Message, state: FSMContext, tab_no: str, _, start_msg_id: int | None):
        await MessageManager.update_main_message(
            message, state, start_msg_id,
            AuthMessageBuilder.enter_password_tab_no_message(tab_no, _), CommonKeyboards.get_back_button_keyboard(_))
        await state.update_data({'login_tab_no': tab_no})
        await state.set_state(Unauthorised.entering_password)

    @staticmethod
    @AuthBaseHandlers.router.message(Unauthorised.entering_password)
    async def process_password(message: Message, state: FSMContext, session, _, bot, login_tab_no, start_msg_id=None):
        employee = await AuthLoginHandlers.auth_service.get_employee_by_tab_no(session, login_tab_no)

        if not AuthLoginHandlers._is_valid_password(employee, message.text):
            await AuthLoginHandlers._handle_invalid_password(message, state, _, start_msg_id)
            return

        await AuthLoginHandlers._handle_successful_login(
            message, state, session, login_tab_no, employee, _, bot, start_msg_id)

    @staticmethod
    def _is_valid_password(employee: Employee, password: str) -> bool:
        return employee.password == password

    @staticmethod
    async def _handle_invalid_password(message: Message, state: FSMContext, _, start_msg_id: int | None):
        await MessageManager.update_main_message(
            message, state, start_msg_id, AuthMessageBuilder.err_wrong_password_message(_),
            CommonKeyboards.get_back_button_keyboard(_))
        await state.set_state(Unauthorised.entering_password)

    @staticmethod
    async def _handle_successful_login(
            message: Message, state: FSMContext, session, tab_no: str, employee, _, bot, start_msg_id=None):
        is_admin = await AuthLoginHandlers.auth_service.is_employee_admin(session, employee.id)
        await state.update_data({'tab_no': tab_no, 'is_admin': is_admin})
        await AuthNavHandlers.authorised_menu(message, state, session, _, bot, tab_no, is_admin, start_msg_id)
