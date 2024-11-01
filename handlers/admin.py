from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter, CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import Text, Bold

from config.env import vsm_logo_uri
from database.orm import add_answer_to_inquiry, get_employee, \
    get_inquiry_with_messages_by_id
from database.update_tg_group_messages import update_tg_group_messages
from filters.is_admin import IsAdmin
from handlers.authorised_start import authorised_start
from handlers.fsm_states import Authorised
from handlers.utils import update_start_message, format_inquiry, move_inquiry_to_archive, \
    update_inquiry_tg_message
from keyboards.inline import get_back_button_keyboard, get_main_admin_keyboard
from logger.logger import logger

admin_router = Router()

@admin_router.message(IsAdmin(), Command('upd_gr'))
async def test_update_tg_group_messages(message, session):
    await update_tg_group_messages(session, message.bot)
    logger.warning('Update tg')

@admin_router.message(StateFilter(Authorised), IsAdmin(), CommandStart())
async def admin_start(message: Message, state: FSMContext, session, _):
    fsm_data = await state.get_data()
    tab_no = fsm_data.get('tab_no')
    employee = await get_employee(session, tab_no)
    welcome_message = Text(
        '\u200B', '\n'
                  '✅ ', Bold(_('Welcome'), ', ', ), '\n',
        Bold('✅ ', employee.full_name), '\n',
        '\u200B',
    )

    if message.text == '/start':
        await message.delete()

        start_msg_id = fsm_data.get('start_msg_id')
        if start_msg_id is not None:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=start_msg_id)
            except TelegramBadRequest:
                ...

        start_msg = await message.answer_photo(
            photo=vsm_logo_uri,
            caption=welcome_message.as_markdown(),
            reply_markup=(await get_main_admin_keyboard(message.bot, _)),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        await state.update_data({'start_msg_id': start_msg.message_id})

    else:
        await update_start_message(
            message, state, welcome_message.as_markdown(), (await get_main_admin_keyboard(message.bot, _)))

    await state.set_state(Authorised.start_menu)

@admin_router.callback_query(StateFilter(Authorised.answering_inquiry), (F.data == 'back_button'))
async def back_button(callback_query: CallbackQuery, state: FSMContext, session, _):
    await authorised_start(callback_query.message, state, session, _)

@admin_router.message(StateFilter(Authorised.answering_inquiry))
async def commit_answer_to_inquiry(message: Message, state: FSMContext, session, _):
    await message.delete()

    fsm_data = await state.get_data()
    inquiry_being_answered_id = fsm_data.get('inquiry_being_answered_id')
    employee = await get_employee(session, fsm_data.get('tab_no'))

    await add_answer_to_inquiry(session, inquiry_being_answered_id, employee.id, message.text)

    inquiry_with_messages = await get_inquiry_with_messages_by_id(session, inquiry_being_answered_id)
    await update_inquiry_tg_message(session, message.bot, inquiry_with_messages)

    await move_inquiry_to_archive(session, message.bot, inquiry_being_answered_id)

    answered_inquiry = await get_inquiry_with_messages_by_id(session, inquiry_being_answered_id)
    await update_start_message(message, state, format_inquiry(answered_inquiry, _).as_markdown(), get_back_button_keyboard(_))
