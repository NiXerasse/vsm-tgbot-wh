from datetime import datetime

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNotFound, TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import StateFilter, CommandStart
from aiogram.utils.formatting import Bold, Text
from babel.dates import get_month_names
from dateutil.relativedelta import relativedelta

from database.orm import get_employee, get_wh_statistics, get_inquiries_by_employee_tab_no
from handlers.fsm_states import Authorised, Unauthorised
from handlers.utils import update_start_message, vsm_logo_uri
from keyboards.inline import get_main_keyboard, get_start_keyboard, get_wh_info_keyboard, get_inquiry_menu_keyboard, \
    get_back_button_keyboard

employee_router = Router()

@employee_router.message(StateFilter(Authorised), CommandStart())
async def cmd_start(message: Message, state: FSMContext, session, _):

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

        start_msg = await message.answer_photo(photo=vsm_logo_uri, caption=welcome_message.as_markdown(), reply_markup=get_main_keyboard(_), parse_mode=ParseMode.MARKDOWN)
        await state.update_data({'start_msg_id': start_msg.message_id})

    else:
        await update_start_message(message, state, welcome_message.as_markdown(), get_main_keyboard(_))

    await state.set_state(Authorised.start_menu)

@employee_router.callback_query(StateFilter(Authorised.start_menu), (F.data == 'log_out_button'))
async def log_out(callback_query: CallbackQuery, state: FSMContext, _):
    await update_start_message(callback_query.message, state, '', get_start_keyboard(_))
    await state.set_state(Unauthorised.start_menu)

@employee_router.callback_query(
    StateFilter(
        Authorised.wh_info, Authorised.inquiry_menu,
        Authorised.entering_inquiry_head, Authorised.entering_inquiry_body
    ),
    (F.data == 'back_button'))
async def back(callback_query: CallbackQuery, state: FSMContext, session, _):
    state_str = await state.get_state()
    if state_str == 'Authorised:entering_inquiry_head':
        await inquiry_menu(callback_query, state, session, _)
    if state_str == 'Authorised:entering_inquiry_body':
        await enter_inquiry_head(callback_query, state, session, _)
    else:
        await cmd_start(callback_query.message, state, session, _)

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
    inquiries_message = Text('🚹 ', _('Here you can write an inquiry regarding employment relations and workflow.'), '\n\n')
    if not inquiries:
        inquiries_message += Text(
            ' 🔘 ', _('You have no inquiries yet.'), '\n'
        )
    else:
        ...
    await update_start_message(callback_query.message, state, inquiries_message.as_markdown(), get_inquiry_menu_keyboard(_))
    state = await state.set_state(Authorised.inquiry_menu)

@employee_router.callback_query(StateFilter(Authorised.inquiry_menu), (F.data == 'write_inquiry'))
async def enter_inquiry_head(callback_query: CallbackQuery, state: FSMContext, session, _):
    enter_inquiry_head_message = Text(
        Bold(
            '🚹 ',
            _('Enter a title for your message. '
              'It will be displayed in the list of requests, so it should be brief and meaningful '), ' ⤵️', '\n'
        )
    )
    await update_start_message(callback_query.message, state, enter_inquiry_head_message.as_markdown(),
                               get_back_button_keyboard(_))
    await state.set_state(Authorised.entering_inquiry_head)

@employee_router.message(StateFilter(Authorised.entering_inquiry_head))
async def process_inquiry_head(message: Message, state: FSMContext, session, _):
    await state.update_data({'inquiry_head': message.text})
    enter_inquiry_body_message = Text(
        Bold(
            '🚹 ',
            _('Enter the text of your inquiry'), ' ⤵️', '\n'
        )
    )
    await update_start_message(message, state, enter_inquiry_body_message.as_markdown(), get_back_button_keyboard(_))
    await state.set_state(Authorised.entering_inquiry_body)
    ...