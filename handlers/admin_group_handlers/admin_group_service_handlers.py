from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from callback_data.admin_group_service_callback_data import RegisterThreadCallback
from config.env import group_command_postfix
from filters.chat_type_filter import ChatTypeFilter
from handlers.admin_group_handlers.admin_group_base_handlers import AdminGroupBaseHandlers
from keyboards.admin_group_service_keyboards import AdminGroupServiceKeyboards
from logger.logger import logger
from services.subdivision_service.subdivision_service import SubdivisionService
from utils.message_builders.admin_group_message_builder import AdminGroupMessageBuilder
from utils.message_manager import MessageManager


class AdminGroupServiceHandlers(AdminGroupBaseHandlers):
    subdivision_service = SubdivisionService()

    @staticmethod
    @AdminGroupBaseHandlers.router.message(
        ChatTypeFilter(chat_type=['group', 'supergroup']),
        Command(f'register{group_command_postfix}'))
    async def registering_message_thread_id(message: Message, session):
        logger.warning('Registering thread')

        register_message = await AdminGroupMessageBuilder.register_message()
        subdivisions = await AdminGroupServiceHandlers.subdivision_service.get_subdivisions(session)
        keyboard = await AdminGroupServiceKeyboards.get_subdivision_thread_register_keyboard(
            subdivisions, message.message_thread_id)

        await MessageManager.answer_message_and_delete(message, register_message, keyboard)

    @staticmethod
    @AdminGroupBaseHandlers.router.callback_query(
        ChatTypeFilter(chat_type=['group', 'supergroup']),
        RegisterThreadCallback.filter())
    async def do_register_message_thread_id(
            callback_query: CallbackQuery, callback_data: RegisterThreadCallback, session):
        await AdminGroupBaseHandlers.adm_grp_msg_service.upsert_subdivision_message_thread(
            session, callback_data.subdivision_id, callback_data.message_thread_id)
        await MessageManager.delete_callback_message_and_alert(callback_query, 'Успешно зарегистрировано!')
