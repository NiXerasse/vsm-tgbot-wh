import asyncio
from datetime import timedelta

from sqlalchemy import select, func, update

from database.models import InquiryMessageMapping, Subdivision, SubdivisionMessageThread, Inquiry
from handlers.utils import admin_group_id
from keyboards.inline import get_inquiry_answer_keyboard
from locales.locales import gettext
from logger.logger import logger


async def update_tg_group_messages(session, bot, hours_older_than=44):
    logger.info('Starting updating group messages')
    time_threshold = func.now() - timedelta(hours=hours_older_than)

    result = await session.execute(
        select(InquiryMessageMapping, Subdivision.name, Inquiry.status)
        .join(SubdivisionMessageThread, InquiryMessageMapping.message_thread_id == SubdivisionMessageThread.message_thread_id)
        .join(Subdivision, SubdivisionMessageThread.subdivision_id == Subdivision.id)
        .join(Inquiry, InquiryMessageMapping.inquiry_id == Inquiry.id)
        .where(InquiryMessageMapping.updated < time_threshold)
    )

    for inq_mes_map, subdivision_name, inquiry_status in result.all():
        if subdivision_name != '.archive':
            logger.warning(f'Updating inquiry tg message: {inq_mes_map.inquiry_id}')
            await bot.edit_message_reply_markup(
                chat_id=admin_group_id,
                message_id=inq_mes_map.message_id,
                reply_markup=get_inquiry_answer_keyboard(inq_mes_map.inquiry_id, gettext['ru'])
            )
            inq_mes_map.updated = func.now()
            await session.merge(inq_mes_map)
        elif 'closed' not in inquiry_status:
            logger.warning(f'Updating archive inquiry tg message: {inq_mes_map.inquiry_id}')
            await bot.edit_message_reply_markup(
                chat_id=admin_group_id,
                message_id=inq_mes_map.message_id,
                reply_markup=None
            )
            new_inquiry_status = inquiry_status + '_closed'
            await session.execute(
                update(Inquiry)
                .where(Inquiry.id == inq_mes_map.inquiry_id)
                .values(status=new_inquiry_status)
            )
        await session.commit()

    logger.info('Finished updating group messages')

async def update_tg_group_messages_loop(interval: int, session, bot, hours_older_than=44):
    try:
        while True:
            await asyncio.shield(update_tg_group_messages(session, bot, hours_older_than))
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        logger.info('Cancelled update_tg_group_messages task')
        raise