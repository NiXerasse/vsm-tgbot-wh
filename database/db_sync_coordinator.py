import asyncio

from debug_tools.logging import async_log_context
from logger.logger import logger
from services.database_sync_service.database_sync_service import DatabaseSyncService
from services.gsheets_service.gsheets_service import GoogleSheetsService
from services.gsheets_sync_service.gsheets_sync_service import GsheetsSyncService


class DatabaseSyncCoordinator:
    def __init__(self, session_maker, gsheets_service: GoogleSheetsService):
        self.session_maker = session_maker
        self.gsheets_service = gsheets_service
        self.gsheets_sync_service = GsheetsSyncService(session_maker, self.gsheets_service)
        self.db_sync_service = DatabaseSyncService(session_maker)

    async def update_all(self):
        async with async_log_context('update_task'):
            async with async_log_context('reading google sheets data'):
                try:
                    await self.gsheets_service.update_files_list()
                    gsheets_data = await self.gsheets_service.get_structured_data()
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logger.warning(f'Error reading google sheets: \n {e}')
                    return

            async with async_log_context('synchronizing db data'):
                await self.db_sync_service.sync_db(gsheets_data)

            async with async_log_context('synchronizing google sheets data (pins)'):
                try:
                    await self.gsheets_sync_service.gsheets_sync()
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    logger.warning(f'Error syncing google sheets: \n {e}')
                    return

    async def update_all_loop(self, interval: int):
        try:
            while True:
                await asyncio.shield(self.update_all())
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logger.info('Cancelled update task')
            raise
