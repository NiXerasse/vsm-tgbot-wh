from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from callback_data.employee_callback_data import ShowInquiryIdCallback, DeleteInquiryIdCallback, \
    DoDeleteInquiryIdCallback, AddMessageInquiryCallback
from config.env import admin_group_id
from handlers.employee_handlers.employee_base_handlers import EmployeeBaseHandlers
from fsm.fsm_states.fsm_states import Authorised
from keyboards.common_keyboards import CommonKeyboards
from keyboards.employee_keyboards import EmployeeKeyboards
from services.admin_group_message_service.admin_group_message_service import AdminGroupMessageService
from services.inquiry_service.inquiry_service import InquiryService
from utils.message_builders.employee_message_builder import EmployeeMessageBuilder
from utils.message_manager import MessageManager


class EmployeeInquiryHandlers(EmployeeBaseHandlers):
    inquiry_service = InquiryService()
    adm_grp_msg_service = AdminGroupMessageService(admin_group_id)

    @staticmethod
    @EmployeeBaseHandlers.router.callback_query(StateFilter(Authorised.start_menu), (F.data == 'inquiry_menu'))
    async def inquiry_menu_handler(callback_query: CallbackQuery, state: FSMContext, session, _, tab_no):
        await EmployeeInquiryHandlers.inquiry_menu(callback_query.message, state, session, _, tab_no)

    @staticmethod
    async def inquiry_menu(message: Message, state: FSMContext, session, _, tab_no):
        inquiries = await EmployeeInquiryHandlers.inquiry_service.get_not_hidden_inquiries_by_employee_tab_no(
            session, tab_no)

        await MessageManager.update_message(
            message, EmployeeMessageBuilder.inquiries_message(inquiries, _),
            EmployeeKeyboards.get_inquiry_menu_keyboard(inquiries, _))

        await state.set_state(Authorised.inquiry_menu)

    @staticmethod
    @EmployeeBaseHandlers.router.callback_query(StateFilter(Authorised.inquiry_menu), ShowInquiryIdCallback.filter())
    async def show_inquiry_handler(
            callback_query: CallbackQuery, callback_data: ShowInquiryIdCallback, state: FSMContext, session, _):

        await EmployeeInquiryHandlers.show_inquiry(callback_query.message, state, session, _, callback_data.inquiry_id)

    @staticmethod
    async def show_inquiry(message: Message, state: FSMContext, session, _, inquiry_id):
        inquiry = await EmployeeInquiryHandlers.inquiry_service.get_inquiry_with_messages_employee_subdivision_by_id(
            session, inquiry_id)

        await MessageManager.update_message(
            message, EmployeeMessageBuilder.inquiry_message(inquiry, _),
            EmployeeKeyboards.get_write_delete_back_button_keyboard(
                inquiry_id, _, add_message_menu=('closed' not in inquiry.status)))

        await EmployeeInquiryHandlers.inquiry_service.make_answered_enquiry_read(session, inquiry)

        await state.set_state(Authorised.viewing_inquiry)

    @staticmethod
    @EmployeeBaseHandlers.router.callback_query(
        StateFilter(Authorised.viewing_inquiry), DeleteInquiryIdCallback.filter())
    async def delete_inquiry(callback_query: CallbackQuery, callback_data: DeleteInquiryIdCallback, state, session, _):
        inquiry_id = callback_data.inquiry_id
        inquiry = await EmployeeInquiryHandlers.inquiry_service.get_inquiry_by_id(session, inquiry_id)

        await MessageManager.update_message(
            callback_query.message, EmployeeMessageBuilder.sure_delete_inquiry_message(inquiry, _),
            EmployeeKeyboards.get_delete_back_button_keyboard(inquiry_id, _))

        await state.set_state(Authorised.deleting_inquiry_last_chance)

    @staticmethod
    @EmployeeBaseHandlers.router.callback_query(
        StateFilter(Authorised.deleting_inquiry_last_chance), DoDeleteInquiryIdCallback.filter())
    async def do_delete_inquiry(
            callback_query: CallbackQuery, callback_data: DoDeleteInquiryIdCallback, state, session, _, bot, tab_no):

        await EmployeeInquiryHandlers._handle_inquiry_deletion(session, callback_data.inquiry_id, bot)

        await EmployeeInquiryHandlers.inquiry_menu(callback_query.message, state, session, _, tab_no)

    @staticmethod
    async def _handle_inquiry_deletion(session, inquiry_id, bot):
        if await EmployeeInquiryHandlers.inquiry_service.has_non_initiator_messages(session, inquiry_id):
            await EmployeeInquiryHandlers.adm_grp_msg_service.move_inquiry_to_archive(session, inquiry_id, bot)
            await EmployeeInquiryHandlers.inquiry_service.hide_inquiry_by_id(session, inquiry_id)
        else:
            await EmployeeInquiryHandlers.adm_grp_msg_service.delete_inquiry_from_admin_group(session, inquiry_id, bot)
            await EmployeeInquiryHandlers.inquiry_service.delete_inquiry_by_id(session, inquiry_id)

    @staticmethod
    @EmployeeBaseHandlers.router.callback_query(
        StateFilter(Authorised.viewing_inquiry), AddMessageInquiryCallback.filter())
    async def write_message_text(
            callback_query: CallbackQuery, callback_data: AddMessageInquiryCallback, state, session, _):

        inquiry = await EmployeeInquiryHandlers.inquiry_service.get_inquiry_by_id(session, callback_data.inquiry_id)

        await MessageManager.update_message(
            callback_query.message, EmployeeMessageBuilder.enter_text_message(inquiry, _),
            CommonKeyboards.get_back_button_keyboard(_))

        await state.update_data({'inquiry_id': inquiry.id})
        await state.set_state(Authorised.adding_message)

    @staticmethod
    @EmployeeBaseHandlers.router.message(Authorised.adding_message)
    async def adding_message_to_inquiry(message: Message, state: FSMContext, session, _, inquiry_id, start_msg_id=None):
        inquiry = await EmployeeInquiryHandlers.inquiry_service.get_inquiry_by_id(session, inquiry_id)
        being_added_message = EmployeeMessageBuilder.being_added_message(inquiry, message.text, _)

        await MessageManager.update_main_message(
            message, state, start_msg_id, being_added_message, EmployeeKeyboards.get_send_back_button_keyboard(_))

        await state.update_data({'being_added_message': message.text})
        await state.set_state(Authorised.sending_message)

    @staticmethod
    @EmployeeBaseHandlers.router.callback_query(StateFilter(Authorised.sending_message), (F.data == 'send_button'))
    async def send_inquiry_with_new_message(
            callback_query: CallbackQuery, state, session, _, bot,  inquiry_id, being_added_message):

        await EmployeeInquiryHandlers.inquiry_service.add_message_to_inquiry(session, inquiry_id, being_added_message)

        inquiry_with_messages = \
            await EmployeeInquiryHandlers.inquiry_service.get_inquiry_with_messages_employee_subdivision_by_id(
                session, inquiry_id)

        await EmployeeInquiryHandlers.adm_grp_msg_service.update_inquiry_admin_group_message(
            session, inquiry_with_messages, _, bot)

        await EmployeeInquiryHandlers.adm_grp_msg_service.move_inquiry_from_archive(session, inquiry_id, bot)

        await EmployeeInquiryHandlers.show_inquiry(callback_query.message, state, session, _, inquiry_id)

    @staticmethod
    @EmployeeBaseHandlers.router.callback_query(StateFilter(Authorised.inquiry_menu), (F.data == 'write_inquiry'))
    async def enter_inquiry_head(callback_query: CallbackQuery, state: FSMContext, _):
        await EmployeeInquiryHandlers.prompt_for_inquiry_head(callback_query, state, _)

    @staticmethod
    async def prompt_for_inquiry_head(callback_query: CallbackQuery, state: FSMContext, _):
        await MessageManager.update_message(
            callback_query.message, EmployeeMessageBuilder.enter_inquiry_head_message(_),
            CommonKeyboards.get_back_button_keyboard(_))
        await state.set_state(Authorised.entering_inquiry_head)

    @staticmethod
    @EmployeeBaseHandlers.router.message(Authorised.entering_inquiry_head)
    async def process_inquiry_head(message: Message, state: FSMContext, _, start_msg_id=None):
        await state.update_data({'inquiry_head_msg_id': message.message_id, 'inquiry_head': message.text})
        await EmployeeInquiryHandlers.prompt_for_inquiry_body(message, state, _, message.text, start_msg_id)

    @staticmethod
    async def prompt_for_inquiry_body(
            message: Message, state: FSMContext, _, inquiry_head, start_msg_id, from_back=False):
        if from_back:
            await MessageManager.update_message(
                message, EmployeeMessageBuilder.enter_inquiry_body_message(inquiry_head , _),
                CommonKeyboards.get_back_button_keyboard(_)
            )
        else:
            await MessageManager.update_main_message(
                message, state, start_msg_id,
                EmployeeMessageBuilder.enter_inquiry_body_message(inquiry_head , _),
                CommonKeyboards.get_back_button_keyboard(_))
        await state.set_state(Authorised.entering_inquiry_body)

    @staticmethod
    @EmployeeBaseHandlers.router.message(Authorised.entering_inquiry_body)
    async def process_inquiry_body(message: Message, state: FSMContext, _, inquiry_head, start_msg_id=None):
        await state.update_data({'inquiry_body_msg_id': message.message_id, 'inquiry_body': message.text})

        await MessageManager.update_main_message(
            message, state, start_msg_id,
            EmployeeMessageBuilder.inquiry_text_message(inquiry_head, message.text),
            EmployeeKeyboards.get_send_back_button_keyboard(_))

        await state.set_state(Authorised.entered_inquiry_body)

    @staticmethod
    @EmployeeBaseHandlers.router.callback_query(StateFilter(Authorised.entered_inquiry_body), (F.data == 'send_button'))
    async def send_inquiry(
            callback_query: CallbackQuery, state: FSMContext, session, _, bot, tab_no, inquiry_head, inquiry_body):

        subdivision, *others = \
            await EmployeeBaseHandlers.employee_service.get_subdivisions_by_employee_tab_no(session, tab_no)
        # TODO If there's more than one subdivision or there's no known subdivision, ask employee to choose

        inquiry = await EmployeeInquiryHandlers.inquiry_service.create_inquiry(
            session, await EmployeeBaseHandlers.employee_service.get_employee_by_tab_no(session, tab_no),
            subdivision.id, inquiry_head, inquiry_body)

        await EmployeeInquiryHandlers.adm_grp_msg_service.publish_inquiry_to_admin_group(session, inquiry, bot)

        await EmployeeInquiryHandlers.inquiry_menu(callback_query.message, state, session, _, tab_no)
