from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Inquiry, InquiryMessageMapping
from keyboards.admin_group_inquiry_keyboards import AdminGroupInquiryKeyboards
from locales.locales import gettext
from repositories.admin_group_message_repository import AdminGroupMessageRepository
from repositories.inquiry_repository import InquiryRepository
from services.subdivision_service.subdivision_service import SubdivisionService
from utils.message_builders.employee_message_builder import EmployeeMessageBuilder

from logger.logger import logger


class AdminGroupMessageService:
    inquiry_repo = InquiryRepository()
    adm_grp_msg_repo = AdminGroupMessageRepository()

    admin_group_id = None

    def __init__(self, admin_group_id):
        AdminGroupMessageService.admin_group_id = admin_group_id

    @staticmethod
    async def move_inquiry_to_archive(session: AsyncSession, inquiry_id, bot):
        service_subdivision_id = await AdminGroupMessageService.adm_grp_msg_repo.get_service_subdivision_id(
            session, SubdivisionService.archive_subdivision)
        message_thread_id = await AdminGroupMessageService.adm_grp_msg_repo.get_message_thread_by_subdivision_id(
            session, service_subdivision_id)
        await AdminGroupMessageService._move_inquiry_to_thread(session, inquiry_id, message_thread_id, bot)

    @staticmethod
    async def _move_inquiry_to_thread(session: AsyncSession, inquiry_id, message_thread_id, bot):
        inq_mess_map = await AdminGroupMessageService.adm_grp_msg_repo.get_inquiry_message_mapping(session, inquiry_id)
        if inq_mess_map.message_thread_id == message_thread_id:
            return

        copied_message = await AdminGroupMessageService._copy_message_to_thread(
            inq_mess_map.message_id, message_thread_id, inquiry_id, bot)

        await AdminGroupMessageService._delete_message_from_admin_group(inq_mess_map.message_id, bot)

        await AdminGroupMessageService.adm_grp_msg_repo.upsert_inquiry_message_mapping(
            session, inquiry_id, copied_message.message_id, message_thread_id)

    @staticmethod
    async def _copy_message_to_thread(message_id, message_thread_id, inquiry_id, bot):
        return await bot.copy_message(
            chat_id=AdminGroupMessageService.admin_group_id,
            from_chat_id=AdminGroupMessageService.admin_group_id,
            message_id=message_id,
            message_thread_id=message_thread_id,
            reply_markup=AdminGroupInquiryKeyboards.get_inquiry_answer_keyboard(inquiry_id, gettext['ru'])
        )

    @staticmethod
    async def move_inquiry_from_archive(session, inquiry_id, bot):
        inquiry = await AdminGroupMessageService.inquiry_repo.get_inquiry_by_id(session, inquiry_id)

        message_thread_id = await AdminGroupMessageService.adm_grp_msg_repo.get_message_thread_by_subdivision_id(
            session, inquiry.subdivision_id)

        await AdminGroupMessageService._move_inquiry_to_thread(session, inquiry_id, message_thread_id, bot)

    @staticmethod
    async def _delete_message_from_admin_group(message_id, bot):
        try:
            await bot.delete_message(
                chat_id=AdminGroupMessageService.admin_group_id,
                message_id=message_id,
            )
        except TelegramBadRequest:
            logger.warning('Error trying to delete old message from admin group...')

    @staticmethod
    async def delete_inquiry_from_admin_group(session: AsyncSession, inquiry_id, bot):
        inq_mess_map = await AdminGroupMessageService.adm_grp_msg_repo.get_inquiry_message_mapping(session, inquiry_id)
        await AdminGroupMessageService._delete_message_from_admin_group(inq_mess_map.message_id, bot)
        await AdminGroupMessageService.adm_grp_msg_repo.delete_inquiry_message_mapping(session, inq_mess_map)

    @staticmethod
    async def update_inquiry_admin_group_message(session: AsyncSession, inquiry_with_messages: Inquiry, _, bot):
        inq_mess_map = await AdminGroupMessageService.adm_grp_msg_repo.get_inquiry_message_mapping(
            session, inquiry_with_messages.id)

        return await bot.edit_message_text(
            chat_id=AdminGroupMessageService.admin_group_id,
            message_id=inq_mess_map.message_id,
            text=EmployeeMessageBuilder.inquiry_message(inquiry_with_messages, _),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=AdminGroupInquiryKeyboards.get_inquiry_answer_keyboard(inquiry_with_messages.id, gettext['ru'])
        )

    @staticmethod
    async def publish_inquiry_to_admin_group(session: AsyncSession, inquiry: Inquiry, bot):
        inq_mess_map = await AdminGroupMessageService.adm_grp_msg_repo.get_inquiry_message_mapping(session, inquiry.id)
        await AdminGroupMessageService._delete_old_admin_group_inquiry_message(inq_mess_map, bot)
        await AdminGroupMessageService._send_inquiry_message_to_admin_group(session, inquiry, inq_mess_map, bot)

    @staticmethod
    async def _delete_old_admin_group_inquiry_message(inq_mess_map: InquiryMessageMapping | None, bot):
        if inq_mess_map is not None:
            try:
                await bot.delete_message(
                    chat_id=AdminGroupMessageService.admin_group_id, message_id=inq_mess_map.message_id)
            except TelegramBadRequest:
                ...

    @staticmethod
    async def _send_inquiry_message_to_admin_group(
            session, inquiry: Inquiry, inq_mess_map: InquiryMessageMapping | None, bot):

        message_thread_id = inq_mess_map.message_thread_id if inq_mess_map is not None else \
            await AdminGroupMessageService.adm_grp_msg_repo.get_message_thread_by_subdivision_id(
                session, inquiry.subdivision_id)

        inquiry_msg =  await bot.send_message(
            chat_id=AdminGroupMessageService.admin_group_id,
            message_thread_id=message_thread_id,
            text=EmployeeMessageBuilder.inquiry_message(inquiry, gettext.get('ru')),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=AdminGroupInquiryKeyboards.get_inquiry_answer_keyboard(inquiry.id, gettext.get('ru'))
        )

        await AdminGroupMessageService.adm_grp_msg_repo.upsert_inquiry_message_mapping(
            session, inquiry.id, inquiry_msg.message_id, message_thread_id)

    @staticmethod
    async def upsert_subdivision_message_thread(session: AsyncSession, subdivision_id: int, message_thread_id: int):
        return await AdminGroupMessageService.adm_grp_msg_repo.upsert_subdivision_message_thread(
            session, subdivision_id, message_thread_id)

    @staticmethod
    async def get_expiring_admin_group_messages(session: AsyncSession, hours_older_than: int):
        return await AdminGroupMessageService.adm_grp_msg_repo.get_expiring_admin_group_messages(
            session, hours_older_than)

    @staticmethod
    async def update_expiring_admin_group_message(bot: Bot, message_id: int, inquiry_id):
        await bot.edit_message_reply_markup(
            chat_id=AdminGroupMessageService.admin_group_id,
            message_id=message_id,
            reply_markup=AdminGroupInquiryKeyboards.get_inquiry_answer_keyboard(inquiry_id, gettext['ru'])
        )

    @staticmethod
    async def delete_buttons_from_expired_admin_group_message(bot, message_id: int):
        await bot.edit_message_reply_markup(
            chat_id=AdminGroupMessageService.admin_group_id,
            message_id=message_id,
            reply_markup=None
        )
