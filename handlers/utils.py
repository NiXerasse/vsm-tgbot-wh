import os

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto, CallbackQuery
from aiogram import types
from aiogram.utils.formatting import Text, Bold

from database.orm import get_inquiry_message_mapping, upsert_inquiry_message_mapping, \
    get_message_thread_by_subdivision_id, get_service_sub_id
from keyboards.inline import get_inquiry_answer_keyboard
from locales.locales import gettext
from logger.logger import logger

vsm_logo_uri = os.getenv('LOGO_URI')
admin_group_id = os.getenv('ADMIN_GROUP_ID')


async def update_start_message(message: Message, state: FSMContext, caption: str, markup: types.InlineKeyboardMarkup | None):
    start_msg_id = (await state.get_data()).get('start_msg_id')
    try:
        await message.bot.edit_message_media(
            media=InputMediaPhoto(
                media=vsm_logo_uri,
                caption=f'\u200B\n{caption}\n\u200B',
                parse_mode='MarkdownV2'
            ),
            chat_id=message.chat.id,
            message_id=start_msg_id,
            reply_markup=markup,
        )
    except TelegramBadRequest:
        logger.warning('Trying to edit message while setting the same content')

def update_callback_query_data(callback_query: CallbackQuery, data: str):
    return CallbackQuery(
        id=callback_query.id,
        from_user=callback_query.from_user,
        message=callback_query.message,
        chat_instance=callback_query.chat_instance,
        data=data
    )

def format_inquiry(inquiry, _ = gettext['ru']):
    inquiry_message = Text(
        Bold(inquiry.employee.full_name), '\n',
        Bold(inquiry.employee.tab_no), '\n',
    )

    initiator = inquiry.employee_id

    inquiry_message += Text(
        Bold(_('Topic'), ': ', inquiry.subject), '\n',
        '\n'
    )

    for msg in inquiry.messages:
        icon = ' ❓ ' if msg.employee_id == initiator else ' ✅ '
        inquiry_message += Text(
            Bold(_('Date'), ': ', msg.sent_at.strftime('%d-%m-%y %H:%M')), '\n',
            icon, msg.content, '\n\n'
        )

    return inquiry_message

async def move_inquiry_to_thread(session, bot, inquiry_with_messages, message_thread_id):
    inq_mess_map = await get_inquiry_message_mapping(session, inquiry_with_messages.id)
    await bot.edit_message_text(
        chat_id=admin_group_id,
        message_id=inq_mess_map.message_id,
        text=format_inquiry(inquiry_with_messages).as_markdown(),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    copied_message = await bot.copy_message(
        chat_id=admin_group_id,
        from_chat_id=admin_group_id,
        message_id=inq_mess_map.message_id,
        message_thread_id=message_thread_id,
    )
    await bot.edit_message_reply_markup(
        chat_id=admin_group_id,
        message_id=copied_message.message_id,
        reply_markup=get_inquiry_answer_keyboard(inquiry_with_messages.id, gettext['ru']),
    )
    await bot.delete_message(
        chat_id=admin_group_id,
        message_id=inq_mess_map.message_id,
    )
    await upsert_inquiry_message_mapping(session, inq_mess_map.inquiry_id, copied_message.message_id, message_thread_id)

async def move_inquiry_to_archive(session, bot, inquiry_with_messages):
    message_thread_id = await get_message_thread_by_subdivision_id(
        session, (await get_service_sub_id(session, '.archive')))
    await move_inquiry_to_thread(session, bot, inquiry_with_messages, message_thread_id)

async def move_inquiry_from_archive(session, bot, inquiry_with_messages):
    message_thread_id = await get_message_thread_by_subdivision_id(session, inquiry_with_messages.subdivision_id)
    await move_inquiry_to_thread(session, bot, inquiry_with_messages, message_thread_id)

async def delete_inquiry_from_admin_group(session, bot, inquiry_id):
    inq_mess_map = await get_inquiry_message_mapping(session, inquiry_id)
    await bot.delete_message(
        chat_id=admin_group_id,
        message_id=inq_mess_map.message_id,
    )
    await session.delete(inq_mess_map)
    await session.commit()
