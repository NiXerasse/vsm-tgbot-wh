from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from callback_data.admin_callback_data import ResetPasswordCallback, ResetPasswordCallbackData
from filters.is_admin import IsAdmin
from fsm.fsm_states.admin_states import AdminResetEmployeePassword
from handlers.admin_handlers.admin_base_handlers import AdminBaseHandlers
from keyboards.admin_keyboards import AdminKeyboards
from keyboards.common_keyboards import CommonKeyboards
from utils.message_builders.admin_message_builder import AdminMessageBuilder
from utils.message_manager import MessageManager


class AdminResetPasswordHandler(AdminBaseHandlers):
    @staticmethod
    @AdminBaseHandlers.router.callback_query(IsAdmin(), ResetPasswordCallback.filter())
    async def prompt_for_employee_tab_no(callback_query: CallbackQuery, state: FSMContext, _):
        await MessageManager.update_message(
            callback_query.message, AdminMessageBuilder.prompt_for_employee_tab_no_message(_),
            CommonKeyboards.get_back_button_keyboard(_))
        await state.set_state(AdminResetEmployeePassword.entering_tab_no)

    @staticmethod
    @AdminBaseHandlers.router.message(
        StateFilter(
            AdminResetEmployeePassword.entering_tab_no,
            AdminResetEmployeePassword.wrong_tab_no
        )
    )
    async def process_entered_tab_no(message: Message, session: AsyncSession, state: FSMContext, start_msg_id, _):
        tab_no = AdminBaseHandlers.employee_service.format_tab_no(message.text)
        employee = await AdminBaseHandlers.employee_service.get_employee_by_tab_no(session, tab_no)
        if employee is None:
            await MessageManager.update_main_message(
                message, state, start_msg_id,
                AdminMessageBuilder.wrong_tab_no_message(tab_no, _),
                CommonKeyboards.get_back_button_keyboard(_)
            )
            await state.set_state(AdminResetEmployeePassword.wrong_tab_no)
        else:
            await MessageManager.update_main_message(
                message, state, start_msg_id,
                AdminMessageBuilder.sure_reset_password_message(employee, _),
                AdminKeyboards.get_reset_password_back_keyboard(employee.id, _)
            )
            await state.set_state(AdminResetEmployeePassword.entered_tab_no)

    @staticmethod
    @AdminBaseHandlers.router.callback_query(
        IsAdmin(),
        AdminResetEmployeePassword.entered_tab_no,
        ResetPasswordCallbackData.filter()
    )
    async def reset_employee_password(
            callback: CallbackQuery, callback_data: ResetPasswordCallbackData,
            session: AsyncSession, state: FSMContext, _
    ):
        employee = await AdminBaseHandlers.employee_service.reset_employee_password(session, callback_data.employee_id)
        await MessageManager.update_message(
            callback.message, AdminMessageBuilder.password_was_reset_message(employee, _),
            CommonKeyboards.get_back_button_keyboard(_)
        )
        await state.set_state(AdminResetEmployeePassword.password_was_reset)
