from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import Text, Bold

from database.orm import add_answer_to_inquiry, get_employee, \
    get_inquiry_with_messages_by_id, get_message_thread_by_subdivision_id, get_service_sub_id
from filters.is_admin import IsAdmin
from handlers.authorised_start import authorised_start
from handlers.fsm_states import Authorised
from handlers.utils import update_start_message, admin_group_id, format_inquiry, vsm_logo_uri
from keyboards.inline import get_back_button_keyboard, get_inquiry_answer_keyboard, get_main_admin_keyboard

admin_router = Router()

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
    answered_inquiry = await get_inquiry_with_messages_by_id(session, inquiry_being_answered_id)

    await update_start_message(message, state, format_inquiry(answered_inquiry, _).as_markdown(), get_back_button_keyboard(_))
    await message.bot.edit_message_text(
        chat_id=admin_group_id,
        message_id=fsm_data.get('message_being_answered_id'),
        text=(format_inquiry(await get_inquiry_with_messages_by_id(session, inquiry_being_answered_id), _).as_markdown()),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    arc_message = await message.bot.copy_message(
        chat_id=admin_group_id,
        from_chat_id=admin_group_id,
        message_id=fsm_data.get('message_being_answered_id'),
        message_thread_id=await get_message_thread_by_subdivision_id(session, (await get_service_sub_id(session, '.archive')))
    )
    await arc_message.edit_text(
        reply_markup=get_inquiry_answer_keyboard(inquiry_being_answered_id, _),
    )
    await message.bot.delete_message(
        chat_id=admin_group_id,
        message_id=fsm_data.get('message_being_answered_id'),
    )
