from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.formatting import Text, Bold
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.env import vsm_logo_uri, group_command_postfix
from database.orm import get_subdivisions, upsert_subdivision_message_thread, get_inquiry_with_messages_by_id
from filters.chat_type_filter import ChatTypeFilter
from filters.is_admin import IsAdmin
from handlers.employee import format_inquiry
from handlers.fsm_states import Authorised
from keyboards.inline import get_back_button_keyboard
from locales.locales import gettext
from logger.logger import logger

admin_group_router = Router()

@admin_group_router.message(
    ChatTypeFilter(chat_type=['group', 'supergroup']),
    Command(f'register{group_command_postfix}'))
async def registering_message_thread_id(message: Message, session):
    logger.warning('Registering thread')
    register_message = Text(
        '🚹 ', Bold('Выберите ОП для регистрации'), ' ⤵️', '\n'
    )

    subdivisions = await get_subdivisions(session)

    keyboard = InlineKeyboardBuilder()
    for subdivision in subdivisions:
        keyboard.add(InlineKeyboardButton(
            text=subdivision.name,
            callback_data=f'register_{group_command_postfix}_{subdivision.id}_{message.message_thread_id}'))

    await message.answer(
        text=register_message.as_markdown(),
        reply_markup=keyboard.adjust(1).as_markup(),
        parse_mode=ParseMode.MARKDOWN)
    await message.delete()

@admin_group_router.callback_query(
    ChatTypeFilter(chat_type=['group', 'supergroup']),
    (F.data.startswith(f'register_{group_command_postfix}')))
async def register_message_thread_id(callback_query: CallbackQuery, session):
    *_, subdivision_id, message_thread_id = callback_query.data.split('_')
    message_thread_id = int(message_thread_id) if message_thread_id != 'None' else 0
    await upsert_subdivision_message_thread(session, int(subdivision_id), message_thread_id)
    await callback_query.message.delete()
    await callback_query.answer(text='Успешно зарегистрировано!', show_alert=True)

@admin_group_router.callback_query(
    IsAdmin(),
    ChatTypeFilter(chat_type=['group', 'supergroup']),
    (F.data.startswith('answer_' + group_command_postfix)))
async def answering_inquiry(callback_query: CallbackQuery, user_state: FSMContext, session):
    user_id = callback_query.from_user.id

    fsm_data = await user_state.get_data()
    _ = gettext[fsm_data.get('locale')]
    inquiry_id = int(callback_query.data.split('_')[-2])
    inquiry = await get_inquiry_with_messages_by_id(session, inquiry_id)
    inquiry_answer_message = Text(
        Bold(_('Write answer for inquiry presented below')), ' ⤵️', '\n\n',
        format_inquiry(inquiry, _)
    )

    start_msg_id = fsm_data.get('start_msg_id')
    if start_msg_id is not None:
        try:
            await callback_query.bot.delete_message(chat_id=user_id, message_id=start_msg_id)
        except TelegramBadRequest:
            ...

    start_msg = await callback_query.bot.send_photo(
        chat_id=user_id,
        photo=vsm_logo_uri,
        caption=inquiry_answer_message.as_markdown(),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_back_button_keyboard(_)
    )
    await user_state.update_data({
        'start_msg_id': start_msg.message_id,
        'inquiry_being_answered_id': inquiry_id,
        'message_being_answered_id': callback_query.message.message_id,
    })
    await user_state.set_state(Authorised.answering_inquiry)

    await callback_query.answer(_('The inquiry has been sent to bot for answering. Go to the bot.'), alert=True)
