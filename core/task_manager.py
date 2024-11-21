import asyncio

from config.env import google_credentials_file, read_file_postfix, admin_group_id
from database.db_sync_coordinator import DatabaseSyncCoordinator
from services.admin_group_message_updater_service.admin_group_message_updater_service import \
    AdminGroupMessageUpdaterService
from services.gsheets_service.gsheets_service import GoogleSheetsService


class TaskManager:
    def __init__(self, session_maker, bot):
        self.session_maker = session_maker
        self.bot = bot

    async def start_tasks(self):
        asyncio.create_task(
            DatabaseSyncCoordinator(
                self.session_maker,
                GoogleSheetsService(google_credentials_file, read_file_postfix)
            ).update_all_loop(interval=60)
        )

        asyncio.create_task(
            AdminGroupMessageUpdaterService(self.session_maker, self.bot, admin_group_id).update_admin_group_messages_loop(
                interval=3600,
                hours_older_than=44
            )
        )
