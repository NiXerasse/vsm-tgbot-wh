from aiogram import F
from aiogram.filters import StateFilter, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from filters.is_admin import IsAdmin
from fsm.fsm_states.admin_states import AdminResetEmployeePassword
from handlers.admin_handlers.admin_base_handlers import AdminBaseHandlers
from fsm.fsm_states.fsm_states import Authorised
from keyboards.admin_keyboards import AdminKeyboards
from utils.message_builders.admin_message_builder import AdminMessageBuilder
from utils.message_manager import MessageManager


class AdminNavHandlers(AdminBaseHandlers):
    @staticmethod
    @AdminBaseHandlers.router.message(StateFilter(Authorised), IsAdmin(), CommandStart())
    async def admin_start(message: Message, state: FSMContext, session, _, bot, tab_no, start_msg_id):
        await AdminNavHandlers.go_to_main_menu(message, state, session, _, bot, tab_no, start_msg_id)

    @staticmethod
    async def go_to_main_menu(
            message: Message, state: FSMContext, session, _, bot, tab_no, start_msg_id=None, from_callback=False):
        if from_callback:
            await MessageManager.update_message(
                message, *(await AdminNavHandlers._get_welcome_parameters(session, _, bot, tab_no)))
        else:
            await MessageManager.update_main_message(
                message, state, start_msg_id,
                *(await AdminNavHandlers._get_welcome_parameters(session, _, bot, tab_no)))
        await state.set_state(Authorised.start_menu)

    @staticmethod
    async def _get_welcome_parameters(session, _, bot, tab_no):
        employee = await AdminBaseHandlers.employee_service.get_employee_by_tab_no(session, tab_no)
        return AdminMessageBuilder.welcome_message(employee, _), await AdminKeyboards.get_main_admin_keyboard(bot, _)

    @staticmethod
    @AdminBaseHandlers.router.callback_query(
        StateFilter(
            Authorised.answering_inquiry, Authorised.answered_inquiry,
            AdminResetEmployeePassword
        ),
        (F.data == 'back_button'))
    async def back_button(callback_query: CallbackQuery, state: FSMContext, session, _, bot, tab_no):
        await AdminNavHandlers.go_to_main_menu(
            callback_query.message, state, session, _, bot, tab_no, from_callback=True)
