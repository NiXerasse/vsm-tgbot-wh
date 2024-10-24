import os

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto, CallbackQuery
from aiogram import types
from aiogram.utils.formatting import Text, Bold

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

def format_inquiry(inquiry, _):
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
