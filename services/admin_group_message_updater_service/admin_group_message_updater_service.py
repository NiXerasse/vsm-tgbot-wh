import asyncio

from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import func

from debug_tools.logging import async_log_context
from logger.logger import logger
from services.admin_group_message_service.admin_group_message_service import AdminGroupMessageService
from services.subdivision_service.subdivision_service import SubdivisionService


class AdminGroupMessageUpdaterService:
    def __init__(self, session_maker, bot, admin_group_id):
        self.adm_grm_msg_service = AdminGroupMessageService(admin_group_id)
        self.session_maker = session_maker
        self.bot = bot

    async def _process_admin_group_message(self, inq_mes_map):
        logger.warning(f'Updating inquiry tg message: {inq_mes_map.inquiry_id}')
        await self.adm_grm_msg_service.update_expiring_admin_group_message(
            self.bot, inq_mes_map.message_id, inq_mes_map.inquiry_id)
        inq_mes_map.updated = func.now()

    async def _process_archive_admin_group_message(self, inq_mes_map, inquiry):
        logger.warning(f'Updating inquiry tg message: {inq_mes_map.inquiry_id}')
        await self.adm_grm_msg_service.delete_buttons_from_expired_admin_group_message(
            self.bot, inq_mes_map.message_id)
        inquiry.status += '_closed'

    async def update_admin_group_messages(self, hours_older_than=44):
        async with async_log_context('updating group messages'), self.session_maker() as session:
            expiring_messages_info = await self.adm_grm_msg_service.get_expiring_admin_group_messages(
                session, hours_older_than)

            for inq_mes_map, subdivision_name, inquiry in expiring_messages_info:
                try:
                    if subdivision_name != SubdivisionService.archive_subdivision:
                        await self._process_admin_group_message(inq_mes_map)
                    elif 'closed' not in inquiry.status:
                        await self._process_archive_admin_group_message(inq_mes_map, inquiry)
                except TelegramBadRequest:  # Message not found
                    await session.delete(inq_mes_map)
                    logger.warning(f'Deleted missing inquiry tg message: {inq_mes_map.inquiry_id}')

            await session.commit()

    async def update_admin_group_messages_loop(self, interval: int, hours_older_than=44):
        try:
            while True:
                await asyncio.shield(self.update_admin_group_messages(hours_older_than))
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info('Cancelled update_tg_group_messages task')
            raise
