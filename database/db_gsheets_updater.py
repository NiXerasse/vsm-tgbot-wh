import asyncio

from database.gsheets import read_google_sheets_data_async, update_google_sheets_data_async
from database.orm import update_db

from logger.logger import logger

async def sync_db_and_gsheets():
    logger.info('Starting update task')
    try:
        data = await read_google_sheets_data_async()
    except asyncio.CancelledError:
        raise
    except Exception as e:
        logger.warning(f'Error reading google sheets: \n {e}')
        return

    await update_db(data)
    try:
        await update_google_sheets_data_async()
    except asyncio.CancelledError:
        raise
    except Exception as e:
        logger.warning(f'Error reading google sheets: \n {e}')
        return
    logger.info('Finished update task')

async def sync_db_and_gsheets_loop(interval: int):
    try:
        while True:
            await asyncio.shield(sync_db_and_gsheets())
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        logger.info('Cancelled update task')
        raise