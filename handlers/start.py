from aiogram import Router, F, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto
from aiogram.utils.formatting import Text, Bold
from aiogram.exceptions import TelegramNotFound

from database.orm import get_employee_by_pin, get_employee, format_tab_no
from handlers.employee import employee_router
from handlers.fsm_states import Unauthorised, Authorised
from handlers.utils import vsm_logo_uri, update_start_message
from keyboards.inline import get_start_keyboard, get_language_selection_keyboard, get_back_button_keyboard, \
    get_got_it_back_button_keyboard, get_save_back_button_keyboard, get_change_login_back_button_keyboard, \
    get_main_keyboard
from locales.locales import gettext
from logger.logger import logger


start_router = Router()
start_router.include_router(employee_router)

vsm_logo = InputMediaPhoto(media=vsm_logo_uri)

@start_router.message(F.photo)
async def get_photo_id(message: types.Message):
    logger.warning(f'Uploaded photo with uri: {message.photo[-1].file_id}')

@start_router.message(StateFilter(Unauthorised), CommandStart())
async def cmd_start(message: Message, state: FSMContext, _):
    await message.delete()

    start_msg_id = (await state.get_data()).get('start_msg_id')

    if start_msg_id is not None:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=start_msg_id)
        except TelegramNotFound:
            ...

    start_msg = await message.answer_photo(photo=vsm_logo_uri, reply_markup=get_start_keyboard(_))
    await state.update_data({'start_msg_id': start_msg.message_id})
    await state.set_state(Unauthorised.start_menu)

@start_router.callback_query(StateFilter(Unauthorised.start_menu), (F.data == 'login_pin'))
async def enter_pin(callback: types.CallbackQuery, state: FSMContext, _):
    enter_pin_message = _("Enter your personal PIN")
    await update_start_message(callback.message, state, f'🔘 *{enter_pin_message}* ⤵️', get_back_button_keyboard(_))
    await state.set_state(Unauthorised.entering_pin)

@start_router.callback_query(StateFilter(Unauthorised.start_menu), (F.data == 'change_language'))
async def change_language(callback: types.CallbackQuery, state: FSMContext, _):
    choose_language_message = _("Choose your language")
    await update_start_message(callback.message, state, f'🔘 *{choose_language_message}* ⤵️', get_language_selection_keyboard(_))
    await state.set_state(Unauthorised.choosing_language)

@start_router.callback_query(StateFilter(Unauthorised.choosing_language), (F.data.startswith('change_language_')))
async def set_language(callback: types.CallbackQuery, state: FSMContext, _):
    language = callback.data[-2:]
    await state.update_data({'locale': language})
    _ = gettext[language]
    await update_start_message(callback.message, state, '', get_start_keyboard(_))
    await state.set_state(Unauthorised.start_menu)

@start_router.callback_query(
    StateFilter(Unauthorised.entering_pin, Unauthorised.correct_pin_entered,
                Unauthorised.entering_new_password, Unauthorised.new_password_entered,
                Unauthorised.entering_password,  Unauthorised.entering_login),
    (F.data == 'back_button'))
async def back_button(callback: types.CallbackQuery, state: FSMContext, _):
    state_str = await state.get_state()
    if state_str == 'Unauthorised:entering_new_password':
        tab_no_msg_id = (await state.get_data()).get('tab_no_msg_id')
        if tab_no_msg_id is not None:
            try:
                await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=tab_no_msg_id)
            except TelegramNotFound:
                ...
        await state.update_data({'tab_no': None, 'tab_no_msg_id': None})

    if state_str == 'Unauthorised:new_password_entered':
        edit_password_message = Text(_('Now you need to enter new password for your account'), ' ⤵️')
        await update_start_message(callback.message, state, edit_password_message.as_markdown(), get_back_button_keyboard(_))
        await state.set_state(Unauthorised.entering_new_password)
    else:
        await update_start_message(callback.message, state, '', get_start_keyboard(_))
        await state.set_state(Unauthorised.start_menu)

@start_router.message(Unauthorised.entering_pin)
async def process_pin(message: Message, state: FSMContext, session, _):
    employee = await get_employee_by_pin(session, message.text.upper())
    if employee is None:
        err_wrong_pin_message = _('You entered a wrong PIN')
        err_wrong_pin_message_2 = _('Please contact your supervisor to get correct PIN')
        await state.set_state(Unauthorised.start_menu)
        await update_start_message(message, state, f'❌ *{err_wrong_pin_message}*\n\n{err_wrong_pin_message_2}', get_start_keyboard(_))
        await message.delete()
        await state.set_state(Unauthorised.start_menu)
        return

    if employee.password:
        err_password_set = Text(
            Bold('❌ ', _('You\'ve already set your password'), '\n'),
            Bold('❌ ', _('Please log in by your username'), '\n')
        )
        await update_start_message(message, state, err_password_set.as_markdown(), get_start_keyboard(_))
        await message.delete()
        await state.set_state(Unauthorised.start_menu)
        return

    welcome_msg = Text(
        '✅ ', _('Hello'), '\n',
        Bold(employee.full_name), '!\n\n',
        _('Your service number'), ': ', Bold(employee.tab_no), '\n\n',
        _('This is your username, which you will use to log into your personal account.'), '\n\n',
        Bold('‼️ ', _('I will keep it below this message'), '!')
    )

    await state.update_data({'tab_no': employee.tab_no})
    await update_start_message(message, state, welcome_msg.as_markdown(), get_got_it_back_button_keyboard(employee.tab_no, _))
    await message.delete()
    await state.set_state(Unauthorised.correct_pin_entered)

@start_router.callback_query(StateFilter(Unauthorised.correct_pin_entered), F.data.startswith('got_it_button_'))
async def enter_new_password(callback: types.CallbackQuery, state: FSMContext, _):
    tab_no = callback.data.split('_')[-1]
    tab_no_msg = await callback.message.answer(text=tab_no)
    await state.update_data({'tab_no_msg_id': tab_no_msg.message_id})
    edit_password_message = Text(_('Now you need to enter new password for your account'), ' ⤵️')
    await update_start_message(callback.message, state, edit_password_message.as_markdown(), get_back_button_keyboard(_))
    await state.set_state(Unauthorised.entering_new_password)

@start_router.callback_query(StateFilter(Unauthorised.entering_password), (F.data == 'change_login'))
async def change_login(callback: types.CallbackQuery, state: FSMContext, _):
    enter_login_message = Text(
        Bold('🔘 ', _('Please enter your username'), ' ⤵️'),
    )
    await update_start_message(callback.message, state, enter_login_message.as_markdown(), get_back_button_keyboard(_))
    await state.set_state(Unauthorised.entering_login)

@start_router.message(Unauthorised.entering_new_password)
async def process_new_password(message: Message, state: FSMContext, _):
    await message.delete()
    password = message.text
    save_password_message = Text('⁉️ ', Bold(_('Your password')), ': ', Bold(password))
    await update_start_message(message, state, save_password_message.as_markdown(), get_save_back_button_keyboard(password, _))
    await state.set_state(Unauthorised.new_password_entered)

@start_router.callback_query(StateFilter(Unauthorised.new_password_entered), F.data.startswith('save_button_'))
async def save_account_data(callback: types.CallbackQuery, state: FSMContext, session, _):
    password = '_'.join(callback.data.split('_')[2:])
    tab_no = (await state.get_data()).get('tab_no')
    employee = await get_employee(session, tab_no)
    employee.password = password
    session.add(employee)
    await session.commit()

    account_saved_message = Text(
        Bold('✅ ', _('Data saved successfully')), '\n',
        _('You can now login by username'), ' ⤵️'
    )
    await update_start_message(callback.message, state, account_saved_message.as_markdown(), get_start_keyboard(_))
    await state.set_state(Unauthorised.start_menu)

@start_router.callback_query(StateFilter(Unauthorised.start_menu), (F.data == 'login_username'))
async def login_username(callback: types.CallbackQuery, state: FSMContext, session, _):
    tab_no = (await state.get_data()).get('tab_no')
    if tab_no is None:
        enter_login_message = Text(
            Bold('🔘 ', _('Please enter your username'), ' ⤵️'),
        )
        await update_start_message(callback.message, state, enter_login_message.as_markdown(), get_back_button_keyboard(_))
        await state.set_state(Unauthorised.entering_login)
        return

    employee = await get_employee(session, tab_no)
    enter_password_message = Text(
        Bold('✅ ', employee.full_name, '\n'),
        Bold('✅ ', employee.tab_no, '\n'),
        '🔘 ', _('Please enter your password'), ' ⤵️'
    )
    await update_start_message(callback.message, state, enter_password_message.as_markdown(), get_change_login_back_button_keyboard(_))
    await state.update_data({'login_tab_no': tab_no})
    await state.set_state(Unauthorised.entering_password)

@start_router.message(Unauthorised.entering_login)
async def process_login(message: Message, state: FSMContext, session, _):
    tab_no = format_tab_no(message.text)
    employee = await get_employee(session, tab_no)

    await message.delete()

    if employee is None:
        err_wrong_tab_no_message = Text(
            Bold('‼️ ', _('You\'ve entered wrong username'), '!\n'),
            Bold('🔘 ', _('Please try again'), ' ⤵️'),
        )

        await update_start_message(message, state, err_wrong_tab_no_message.as_markdown(), get_back_button_keyboard(_))
        await state.set_state(Unauthorised.entering_login)
        return

    enter_password_message = Text(
        '✅ ', Bold(_('Username'), ': ', tab_no), '\n',
        '🔘 ', _('Please enter your password'), ' ⤵️'
    )
    await update_start_message(message, state, enter_password_message.as_markdown(), get_back_button_keyboard(_))
    await state.update_data({'login_tab_no': tab_no})
    await state.set_state(Unauthorised.entering_password)

@start_router.message(Unauthorised.entering_password)
async def process_password(message: Message, state: FSMContext, session, _):
    await message.delete()

    tab_no = (await state.get_data()).get('login_tab_no')
    password = message.text
    employee = await get_employee(session, tab_no)
    if employee.password != password:
        err_wrong_password_message = Text(
            Bold('‼️ ', _('You\'ve entered wrong password'), '!\n'),
            Bold('🔘 ', _('Please try again'), ' ⤵️'),
        )
        await update_start_message(message, state, err_wrong_password_message.as_markdown(), get_back_button_keyboard(_))
        await state.set_state(Unauthorised.entering_password)
        return

    welcome_message = Text(
        '✅ ', Bold(_('Welcome'), ', ', ), '\n',
        Bold('✅ ', employee.full_name),
    )
    await update_start_message(message, state, welcome_message.as_markdown(), get_main_keyboard(_))

    await state.update_data({'tab_no': tab_no})
    await state.set_state(Authorised.start_menu)
