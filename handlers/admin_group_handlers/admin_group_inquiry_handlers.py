from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from callback_data.admin_group_inquiry_callback_data import InquiryAnswerCallback
from filters.chat_type_filter import ChatTypeFilter
from filters.is_admin import IsAdmin
from handlers.admin_group_handlers.admin_group_base_handlers import AdminGroupBaseHandlers
from fsm.fsm_states.fsm_states import Authorised
from keyboards.common_keyboards import CommonKeyboards
from locales.locales import gettext
from services.inquiry_service.inquiry_service import InquiryService
from utils.message_builders.admin_group_message_builder import AdminGroupMessageBuilder
from utils.message_builders.employee_message_builder import EmployeeMessageBuilder
from utils.message_manager import MessageManager


class AdminGroupInquiryHandlers(AdminGroupBaseHandlers):
    inquiry_service = InquiryService()

    @staticmethod
    @AdminGroupBaseHandlers.router.callback_query(
        IsAdmin(),
        ChatTypeFilter(chat_type=['group', 'supergroup']),
        InquiryAnswerCallback.filter())
    async def answering_inquiry(
            callback_query: CallbackQuery, callback_data: InquiryAnswerCallback, user_state: FSMContext, session, bot):
        user_id = callback_query.from_user.id
        start_msg_id, _ = (await user_state.get_data()).get('start_msg_id'), gettext['ru']

        inquiry = \
            await AdminGroupInquiryHandlers.inquiry_service.get_inquiry_with_messages_employee_subdivision_by_id(
                session, callback_data.inquiry_id)
        inquiry_answer_message = AdminGroupMessageBuilder.inquiry_answer_message(
            EmployeeMessageBuilder.inquiry_message(inquiry, _), _)

        start_msg = await MessageManager.update_main_message_from_outer_space(
            bot, user_id, start_msg_id, inquiry_answer_message, CommonKeyboards.get_back_button_keyboard(_))

        await user_state.update_data({
            'start_msg_id': start_msg.message_id,
            'inquiry_being_answered_id': inquiry.id,
            'message_being_answered_id': callback_query.message.message_id,
        })
        await user_state.set_state(Authorised.answering_inquiry)

        await callback_query.answer(_('The inquiry has been sent to bot for answering. Go to the bot.'), alert=True)
