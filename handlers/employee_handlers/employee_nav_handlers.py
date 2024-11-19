from aiogram import F
from aiogram.filters import StateFilter, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from handlers.employee_handlers.employee_base_handlers import EmployeeBaseHandlers
from handlers.employee_handlers.employee_inquiry_handlers import EmployeeInquiryHandlers
from fsm.fsm_states.fsm_states import Authorised, Unauthorised
from keyboards.auth_keyboards import AuthKeyboards
from keyboards.employee_keyboards import EmployeeKeyboards
from utils.message_builders.employee_message_builder import EmployeeMessageBuilder
from utils.message_manager import MessageManager


class EmployeeNavHandlers(EmployeeBaseHandlers):
    @staticmethod
    @EmployeeBaseHandlers.router.message(StateFilter(Authorised), CommandStart())
    async def cmd_start(message: Message, state: FSMContext, session, _, tab_no, start_msg_id=None):
        await EmployeeNavHandlers.go_to_main_menu(message, state, session, _, tab_no, start_msg_id)

    @staticmethod
    async def go_to_main_menu(
            message: Message, state: FSMContext, session, _, tab_no, start_msg_id=None, from_callback=False):
        if from_callback:
            await MessageManager.update_message(
                message, *(await EmployeeNavHandlers._get_welcome_parameters(session, _, tab_no)))
        else:
            await MessageManager.update_main_message(
                message, state, start_msg_id, *(await EmployeeNavHandlers._get_welcome_parameters(session, _, tab_no)))
        await state.set_state(Authorised.start_menu)

    @staticmethod
    async def _get_welcome_parameters(session, _, tab_no):
        employee = await EmployeeBaseHandlers.employee_service.get_employee_by_tab_no(session, tab_no)
        has_answers = await EmployeeBaseHandlers.employee_service.has_answered_inquiries(session, employee.id)
        return EmployeeMessageBuilder.welcome_message(employee, _), EmployeeKeyboards.get_main_keyboard(has_answers, _)

    @staticmethod
    @EmployeeBaseHandlers.router.callback_query(StateFilter(Authorised.start_menu), (F.data == 'log_out_button'))
    async def log_out(callback_query: CallbackQuery, state: FSMContext, _):
        await MessageManager.update_message(
            callback_query.message, '', AuthKeyboards.get_start_keyboard(_))
        await state.update_data({'is_admin': False})
        await state.set_state(Unauthorised.start_menu)

    @staticmethod
    @EmployeeBaseHandlers.router.callback_query(StateFilter(Authorised), (F.data == 'back_button'))
    async def back(
            callback_query: CallbackQuery, state: FSMContext, session, _,
            tab_no, inquiry_head=None, start_msg_id=None):
        state_str = await state.get_state()
        message = callback_query.message
        if state_str in ['Authorised:entering_inquiry_head', 'Authorised:viewing_inquiry',
                         'Authorised:deleting_inquiry_last_chance', 'Authorised:adding_message',
                         'Authorised:sending_message']:
            await EmployeeInquiryHandlers.inquiry_menu(message, state, session, _, tab_no)
        elif state_str == 'Authorised:entering_inquiry_body':
            await EmployeeInquiryHandlers.prompt_for_inquiry_head(callback_query, state, _)
        elif state_str == 'Authorised:entered_inquiry_body':
            await EmployeeInquiryHandlers.prompt_for_inquiry_body(
                callback_query.message, state, _, inquiry_head, start_msg_id, from_back=True)
        # elif state_str in ['Authorised.wh_detailed_info', 'Authorised.wh_rate_info']:
        #     ...
        else:
            await EmployeeNavHandlers.go_to_main_menu(message, state, session, _, tab_no, from_callback=True)
