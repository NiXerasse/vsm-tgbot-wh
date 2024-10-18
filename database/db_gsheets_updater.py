import asyncio

from database.gsheets import read_google_sheets_data_async, update_google_sheets_data_async
from database.orm import update_db
from logger.logger import logger

async def sync_db_and_gsheets():
    logger.info('Starting update task')
    data = await read_google_sheets_data_async()
    await update_db(data)
    await update_google_sheets_data_async()
    logger.info('Finished update task')

async def sync_db_and_gsheets_loop(interval: int):
    try:
        while True:
            await asyncio.shield(sync_db_and_gsheets())
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        logger.info('Cancelled update task')
        raise