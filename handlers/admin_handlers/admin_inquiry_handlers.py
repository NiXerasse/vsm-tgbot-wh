from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config.env import admin_group_id
from handlers.admin_handlers.admin_base_handlers import AdminBaseHandlers
from fsm.fsm_states.fsm_states import Authorised
from keyboards.common_keyboards import CommonKeyboards
from services.admin_group_message_service.admin_group_message_service import AdminGroupMessageService
from services.inquiry_service.inquiry_service import InquiryService
from utils.message_builders.admin_message_builder import AdminMessageBuilder
from utils.message_builders.employee_message_builder import EmployeeMessageBuilder
from utils.message_manager import MessageManager


class AdminInquiryHandlers(AdminBaseHandlers):
    inquiry_service = InquiryService()
    adm_grp_msg_service = AdminGroupMessageService(admin_group_id)

    @staticmethod
    @AdminBaseHandlers.router.message(StateFilter(Authorised.answering_inquiry))
    async def commit_answer_to_inquiry(
            message: Message, state: FSMContext, session, _, tab_no, inquiry_being_answered_id, bot, start_msg_id=None):

        inquiry_with_messages = \
            await AdminInquiryHandlers._handle_answer_inquiry(
                session, inquiry_being_answered_id, message.text, _, tab_no, bot)

        await MessageManager.update_main_message(
            message, state, start_msg_id,
            AdminMessageBuilder.inquiry_answered_message(
                EmployeeMessageBuilder.inquiry_message(inquiry_with_messages, _), _),
            CommonKeyboards.get_back_button_keyboard(_)
        )

        await state.set_state(Authorised.answered_inquiry)

    @staticmethod
    async def _handle_answer_inquiry(session, inquiry_being_answered_id, answer, _, tab_no, bot):
        employee = await AdminInquiryHandlers.employee_service.get_employee_by_tab_no(session, tab_no)

        await AdminInquiryHandlers.inquiry_service.add_answer_to_inquiry(
            session, inquiry_being_answered_id, employee.id, answer)

        inquiry_with_messages = \
            await AdminInquiryHandlers.inquiry_service.get_inquiry_with_messages_employee_subdivision_by_id(
                session, inquiry_being_answered_id)
        await AdminInquiryHandlers.adm_grp_msg_service.update_inquiry_admin_group_message(
            session, inquiry_with_messages, _, bot)
        await AdminInquiryHandlers.adm_grp_msg_service.move_inquiry_to_archive(session, inquiry_being_answered_id, bot)

        return inquiry_with_messages
