from aiogram import F, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from filters.is_admin import IsAdmin
from keyboards.auth_keyboards import AuthKeyboards
from keyboards.common_keyboards import CommonKeyboards
from .auth_base_handlers import AuthBaseHandlers
from fsm.fsm_states.fsm_states import Unauthorised
from utils.message_builders.auth_message_builder import AuthMessageBuilder
from utils.message_manager import MessageManager


class AuthNavHandlers(AuthBaseHandlers):
    @staticmethod
    @AuthBaseHandlers.router.message(StateFilter(Unauthorised, None), CommandStart())
    async def cmd_start(message: Message, state: FSMContext, _, start_msg_id=None):
        await MessageManager.update_main_message(
            message, state, start_msg_id, keyboard=AuthKeyboards.get_start_keyboard(_))
        await state.set_state(Unauthorised.start_menu)

    @staticmethod
    @AuthBaseHandlers.router.callback_query(
        StateFilter(Unauthorised.entering_pin, Unauthorised.correct_pin_entered,
                    Unauthorised.entering_new_password, Unauthorised.new_password_entered,
                    Unauthorised.entering_password, Unauthorised.entering_login),
        (F.data == 'back_button'))
    async def back_button(callback: types.CallbackQuery, state: FSMContext, _, tab_no_msg_id=None):
        state_str = await state.get_state()

        state_handlers = {
            'Unauthorised:entering_new_password':
                (AuthNavHandlers._handle_back_entering_new_password, (tab_no_msg_id,)),
            'Unauthorised:new_password_entered':
                (AuthNavHandlers._handle_back_new_password_entered, ()),
        }

        handler, params = state_handlers.get(state_str, (AuthNavHandlers._default_back_handler, ()))
        await handler(callback, state, _, *params)

    @staticmethod
    async def _handle_back_entering_new_password(callback: types.CallbackQuery, state: FSMContext, _, tab_no_msg_id):
        # tab_no_msg_id = (await state.get_data()).get('tab_no_msg_id')
        if tab_no_msg_id is not None:
            try:
                await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=tab_no_msg_id)
            except TelegramBadRequest:
                pass
        await state.update_data({'tab_no': None, 'tab_no_msg_id': None})
        await AuthNavHandlers._go_to_start_menu_from_callback(callback, state, _)

    @staticmethod
    async def _handle_back_new_password_entered(callback: types.CallbackQuery, state: FSMContext, _):
        await MessageManager.update_message(
            callback.message, AuthMessageBuilder.edit_password_message(_), CommonKeyboards.get_back_button_keyboard(_))
        await state.set_state(Unauthorised.entering_new_password)

    @staticmethod
    async def _default_back_handler(callback: types.CallbackQuery, state: FSMContext, _):
        await AuthNavHandlers._go_to_start_menu_from_callback(callback, state, _)

    @staticmethod
    async def _go_to_start_menu_from_callback(callback: types.CallbackQuery, state: FSMContext, _):
        await MessageManager.update_message(
            callback.message, '', AuthKeyboards.get_start_keyboard(_))
        await state.set_state(Unauthorised.start_menu)

    @staticmethod
    async def authorised_menu(
            message: Message, state: FSMContext, session, _, bot, tab_no, is_admin, start_msg_id=None):
        if await IsAdmin()(message, is_admin):
            from handlers.admin_handlers.admin_nav_handlers import AdminNavHandlers
            await AdminNavHandlers.go_to_main_menu(message, state, session, _, bot, tab_no, start_msg_id)
        else:
            from handlers.employee_handlers.employee_nav_handlers import EmployeeNavHandlers
            await EmployeeNavHandlers.go_to_main_menu(message, state, session, _, tab_no, start_msg_id)
