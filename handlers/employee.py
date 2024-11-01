from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter, CommandStart
from aiogram.utils.formatting import Bold, Text
from babel.dates import get_month_names
from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession

from config.env import vsm_logo_uri, admin_group_id
from database.models import Inquiry
from database.orm import get_employee, get_wh_statistics, get_inquiries_by_employee_tab_no, create_inquiry, \
    get_inquiry_with_messages_by_id, get_inquiry_by_id, delete_inquiry_by_id, add_message_to_inquiry, \
    get_subdivisions_by_employee_tab_no, get_message_thread_by_subdivision_id, upsert_inquiry_message_mapping, \
    get_inquiry_message_mapping, has_answered_inquiries, update_inquiry_status, has_non_initiator_messages, \
    set_inquiry_status
from handlers.authorised_start import authorised_start
from handlers.fsm_states import Authorised, Unauthorised
from handlers.utils import update_start_message, update_callback_query_data,  \
    format_inquiry, move_inquiry_from_archive, delete_inquiry_from_admin_group, move_inquiry_to_archive, \
    update_inquiry_tg_message
from keyboards.inline import get_main_keyboard, get_start_keyboard, get_wh_info_keyboard, get_inquiry_menu_keyboard, \
    get_back_button_keyboard, get_send_back_button_keyboard, \
    get_write_delete_back_button_keyboard, get_delete_back_button_keyboard, get_inquiry_answer_keyboard
from locales.locales import gettext

employee_router = Router()

@employee_router.message(StateFilter(Authorised), CommandStart())
async def employee_cmd_start(message: Message, state: FSMContext, session, _):
    fsm_data = await state.get_data()
    tab_no = fsm_data.get('tab_no')
    employee = await get_employee(session, tab_no)
    welcome_message = Text(
        '\u200B', '\n'
        '✅ ', Bold(_('Welcome'), ', ', ), '\n',
        Bold('✅ ', employee.full_name), '\n',
        '\u200B',
    )

    has_answers = await has_answered_inquiries(session, employee.id)

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
            reply_markup=get_main_keyboard(has_answers, _),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        await state.update_data({'start_msg_id': start_msg.message_id})

    else:
        await update_start_message(message, state, welcome_message.as_markdown(), get_main_keyboard(has_answers, _))

    await state.set_state(Authorised.start_menu)

@employee_router.callback_query(StateFilter(Authorised.start_menu), (F.data == 'log_out_button'))
async def log_out(callback_query: CallbackQuery, state: FSMContext, _):
    await update_start_message(callback_query.message, state, '', get_start_keyboard(_))
    await state.update_data({'is_admin': False})
    await state.set_state(Unauthorised.start_menu)

@employee_router.callback_query(
    StateFilter(
        Authorised.wh_info, Authorised.inquiry_menu,
        Authorised.entering_inquiry_head, Authorised.entering_inquiry_body,
        Authorised.entered_inquiry_body, Authorised.viewing_inquiry,
        Authorised.deleting_inquiry_last_chance, Authorised.adding_message,
        Authorised.sending_message
    ),
    (F.data == 'back_button'))
async def back(callback_query: CallbackQuery, state: FSMContext, session, _):
    state_str = await state.get_state()
    message = callback_query.message
    if state_str in ['Authorised:entering_inquiry_head', 'Authorised:viewing_inquiry',
                     'Authorised:deleting_inquiry_last_chance', 'Authorised:adding_message',
                     'Authorised:sending_message']:
        new_callback_query = update_callback_query_data(callback_query, 'inquiry_menu')
        await inquiry_menu(new_callback_query, state, session, _)
    elif state_str == 'Authorised:entering_inquiry_body':
        new_callback_query = update_callback_query_data(callback_query, 'write_inquiry')
        await enter_inquiry_head(new_callback_query, state, _)
    elif state_str == 'Authorised:entered_inquiry_body':
        await enter_inquiry_body(callback_query.message, state, _)
    else:
        await authorised_start(message, state, session, _)

@employee_router.callback_query(StateFilter(Authorised.start_menu), (F.data == 'get_wh_info'))
async def get_wh_info(callback_query: CallbackQuery, state: FSMContext, session, _):
    fsm_data = await state.get_data()
    tab_no, locale = fsm_data.get('tab_no'), fsm_data.get('locale', 'en')
    employee = await get_employee(session, tab_no)

    now = datetime.now()
    target_date = (now - relativedelta(months=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    target_month = target_date.month
    target_year = target_date.year

    target_period_start = target_date.replace(day=1)
    target_period_end = target_period_start + relativedelta(months=1)

    wh_stats = await get_wh_statistics(session, tab_no, target_period_start, target_period_end)

    target_month_str = get_month_names(context='stand-alone', locale=locale)[target_month]
    wh_info_message = Text(
        '🚹 ', Bold(employee.full_name), '\n',
        '🚹 ', Bold(tab_no), '\n',
        '🚹 ', Bold(_('Data for'), ' ', target_month_str.capitalize(), '\'', target_year % 100), '\n',
        '\n',
    )

    for wh_stat in wh_stats:
        wh_info_subdivision = Text(
            '✅ ', Bold(wh_stat['subdivision_name'], ': '), '\n',
            ' 🔘 ', _('Number of days worked'), ': ', wh_stat['count_nonzero'], '\n',
            ' 🔘 ', _('Accounted hours'), ': ', wh_stat['sum_total'],
            '\n',
        )
        wh_info_message += wh_info_subdivision

    await update_start_message(callback_query.message, state, wh_info_message.as_markdown(), get_wh_info_keyboard(_))
    await state.set_state(Authorised.wh_info)

@employee_router.callback_query(StateFilter(Authorised.start_menu), (F.data == 'inquiry_menu'))
async def inquiry_menu(callback_query: CallbackQuery, state: FSMContext, session, _):
    tab_no = (await state.get_data()).get('tab_no')
    inquiries = await get_inquiries_by_employee_tab_no(session, tab_no)
    inquiries = [inquiry for inquiry in inquiries if 'hidden' not in inquiry.status]

    inquiries_message = Text()
    if not inquiries:
        inquiries_message = Text(
            '🚹 ', _('Here you can write an inquiry regarding employment relations and workflow.'), '\n\n')
        inquiries_message += Text(
            ' 🔘 ', _('You have no inquiries yet.'), '\n'
        )
    else:
        inquiries_message += Text('🚹 ', Bold(_('Your inquiries'), ': '), '\n\n')
        for i, inquiry in enumerate(inquiries, start=1):
            bullet = ' 🟢 ' if inquiry.status == 'answered' else ' 🔘 ' if inquiry.status == 'closed' else ' 🟣 '
            inquiries_message += Text(
                bullet, f'{i}. ', Bold(inquiry.subject), '\n',
            )
        inquiries_message += Text(
            '\n\n',
            Bold('🚹 ', _('To work with inquiry press a button with corresponding number below'), ' ⤵️', '\n')
        )
    await update_start_message(callback_query.message, state, inquiries_message.as_markdown(), get_inquiry_menu_keyboard(inquiries, _))
    await state.set_state(Authorised.inquiry_menu)

@employee_router.callback_query(StateFilter(Authorised.inquiry_menu), (F.data.startswith('inquiry_menu_')))
async def show_inquiry(callback_query: CallbackQuery, state: FSMContext, session, _):
    inquiry_id = int(callback_query.data.split('_')[-1])
    inquiry = await get_inquiry_with_messages_by_id(session, inquiry_id)
    await update_start_message(
        callback_query.message, state, format_inquiry(inquiry, _).as_markdown(),
        get_write_delete_back_button_keyboard(inquiry_id, _, add_message_menu=(inquiry.status != 'closed')))
    await state.set_state(Authorised.viewing_inquiry)
    if inquiry.status == 'answered':
        await update_inquiry_status(session, inquiry_id, 'answered_and_read')

@employee_router.callback_query(StateFilter(Authorised.viewing_inquiry), (F.data.startswith('delete_inquiry_')))
async def delete_inquiry(callback_query: CallbackQuery, state, session, _):
    inquiry_id = int(callback_query.data.split('_')[-1])
    inquiry = await get_inquiry_by_id(session, inquiry_id)
    are_you_sure_message = Text(
        Bold('⁉️ ', _('The inquiry'), ': ', '\n\n'),
        Bold('⁉️', inquiry.subject), '\n\n',
        Bold('⁉️ ', _('will be deleted'), '!', '\n')
    )
    await update_start_message(callback_query.message, state, are_you_sure_message.as_markdown(),
                               get_delete_back_button_keyboard(inquiry_id, _))
    await state.set_state(Authorised.deleting_inquiry_last_chance)

@employee_router.callback_query(StateFilter(Authorised.deleting_inquiry_last_chance), (F.data.startswith('delete_inquiry_')))
async def do_delete_inquiry(callback_query: CallbackQuery, state, session, _):
    inquiry_id = int(callback_query.data.split('_')[-1])
    if await has_non_initiator_messages(session, inquiry_id):
        new_inquiry_status = (await get_inquiry_by_id(session, inquiry_id)).status + "_hidden"
        await set_inquiry_status(session, inquiry_id, new_inquiry_status)
        await move_inquiry_to_archive(session, callback_query.bot, inquiry_id)
    else:
        await delete_inquiry_by_id(session, inquiry_id)
        await delete_inquiry_from_admin_group(session, callback_query.bot, inquiry_id)
    new_callback_query = update_callback_query_data(callback_query, 'inquiry_menu')
    await inquiry_menu(new_callback_query, state, session, _)

@employee_router.callback_query(StateFilter(Authorised.viewing_inquiry), (F.data.startswith('add_message_')))
async def write_message_text(callback_query: CallbackQuery, state, session, _):
    inquiry_id = int(callback_query.data.split('_')[-1])
    inquiry = await get_inquiry_by_id(session, inquiry_id)
    enter_text_message = Text(
        Bold('🚹 ', _('Enter a text for your inquiry with topic'), ': ⤵️'),
        '\n\n',
        Bold(' 🟣 ', inquiry.subject),
    )

    await update_start_message(callback_query.message, state, enter_text_message.as_markdown(), get_back_button_keyboard(_))
    await state.update_data({'inquiry_id': inquiry_id})
    await state.set_state(Authorised.adding_message)

@employee_router.message(Authorised.adding_message)
async def adding_message_to_inquiry(message: Message, state: FSMContext, session, _):
    fsm_data = await state.get_data()
    inquiry_id = fsm_data['inquiry_id']
    inquiry = await get_inquiry_by_id(session, inquiry_id)
    being_added_message = Text(
        '🚹 ', _('You are adding the message to the inquiry with topic'), ': ', '\n',
        Bold(' 🟣 ', inquiry.subject), '\n\n',
        Bold('🚹 ', _('Content of the message'), ': '), '\n',
        ' 🔘 ', message.text, '\n'
    )

    await update_start_message(message, state, being_added_message.as_markdown(), get_send_back_button_keyboard(_))
    await message.delete()
    await state.update_data({'being_added_message': message.text})
    await state.set_state(Authorised.sending_message)

@employee_router.callback_query(StateFilter(Authorised.sending_message), (F.data == 'send_button'))
async def send_inquiry_with_new_message(callback_query: CallbackQuery, state, session, _):
    fsm_data = await state.get_data()
    inquiry_id = fsm_data['inquiry_id']
    message_text = fsm_data['being_added_message']
    await add_message_to_inquiry(session, inquiry_id, message_text)
    await update_inquiry_tg_message(
        session, callback_query.bot,
        await get_inquiry_with_messages_by_id(session, inquiry_id))
    await move_inquiry_from_archive(session, callback_query.bot, inquiry_id)

    new_callback_query = update_callback_query_data(callback_query, f'inquiry_menu_{inquiry_id}')
    await show_inquiry(new_callback_query, state, session, _)

@employee_router.callback_query(StateFilter(Authorised.inquiry_menu), (F.data == 'write_inquiry'))
async def enter_inquiry_head(callback_query: CallbackQuery, state: FSMContext, _):
    enter_inquiry_head_message = Text(
        Bold('🚹 ', _('Enter a topic for your inquiry.')),
        '\n\n',
        _('It will be displayed in the list of requests, so it should be brief and meaningful.'), ' ⤵️', '\n'
    )
    await update_start_message(callback_query.message, state, enter_inquiry_head_message.as_markdown(),
                               get_back_button_keyboard(_))
    await state.set_state(Authorised.entering_inquiry_head)

@employee_router.message(Authorised.entering_inquiry_head)
async def process_inquiry_head(message: Message, state: FSMContext, _):
    await state.update_data({'inquiry_head_msg_id': message.message_id, 'inquiry_head': message.text})
    await enter_inquiry_body(message, state, _)
    await message.bot.delete_message(message.chat.id, (await state.get_data())['inquiry_head_msg_id'])

async def enter_inquiry_body(message: Message, state: FSMContext, _):
    enter_inquiry_body_message = Text(
        Bold(
            '🚹 ',
            _('Enter the text for the inquiry with topic'), ': ', '\n\n',
            ' 🟣 ', (await state.get_data())['inquiry_head'], ' ⤵️', '\n'
        )
    )
    await update_start_message(message, state, enter_inquiry_body_message.as_markdown(), get_back_button_keyboard(_))
    await state.set_state(Authorised.entering_inquiry_body)

@employee_router.message(Authorised.entering_inquiry_body)
async def process_inquiry_body(message: Message, state: FSMContext, _):
    fsm_data = await state.get_data()
    await state.update_data({'inquiry_body_msg_id': message.message_id, 'inquiry_body': message.text})
    inquiry_text_message = Text(
        '✅ ', Bold(fsm_data['inquiry_head']), '\n\n',
        ' 🟣 ', message.text, '\n'
    )

    await update_start_message(message, state, inquiry_text_message.as_markdown(), get_send_back_button_keyboard(_))
    await state.set_state(Authorised.entered_inquiry_body)
    await message.bot.delete_message(message.chat.id, (await state.get_data())['inquiry_body_msg_id'])

@employee_router.callback_query(StateFilter(Authorised.entered_inquiry_body), (F.data == 'send_button'))
async def send_inquiry(callback_query: CallbackQuery, state: FSMContext, session, _):
    fsm_data = await state.get_data()
    subdivision, *others = await get_subdivisions_by_employee_tab_no(session, fsm_data['tab_no'])
    # TODO If there's more than one subdivision or there's no known subdivision, ask employee to choose

    inquiry = await create_inquiry(session, fsm_data['tab_no'], subdivision.id, fsm_data['inquiry_head'], fsm_data['inquiry_body'])
    await publish_inquiry_to_admin_group(session, callback_query.bot, inquiry)

    new_callback_query = update_callback_query_data(callback_query, 'inquiry_menu')
    await inquiry_menu(new_callback_query, state, session, _)

async def publish_inquiry_to_admin_group(session: AsyncSession, bot: Bot, inquiry: Inquiry):
    inq_mess_map = await get_inquiry_message_mapping(session, inquiry.id)
    if inq_mess_map is not None:
        try:
            await bot.delete_message(
                chat_id=admin_group_id,
                message_id=inq_mess_map.message_id,
            )
        except TelegramBadRequest:
            ...

    message_thread_id = inq_mess_map.message_thread_id \
        if inq_mess_map is not None \
        else (await get_message_thread_by_subdivision_id(session, inquiry.subdivision_id))

    inquiry_msg = await bot.send_message(
        chat_id=admin_group_id,
        message_thread_id=message_thread_id,
        text=format_inquiry(inquiry, gettext.get('ru')).as_markdown(),
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=get_inquiry_answer_keyboard(inquiry.id, gettext.get('ru'))
    )

    await upsert_inquiry_message_mapping(session, inquiry.id, inquiry_msg.message_id, message_thread_id)
