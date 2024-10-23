from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.formatting import Text, Bold
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.orm import get_subdivisions, upsert_subdivision_message_thread, get_user_data
from filters.chat_type_filter import ChatTypeFilter
from logger.logger import logger

admin_group_router = Router()

@admin_group_router.message(ChatTypeFilter(chat_type=['group', 'supergroup']), Command('register'))
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
            callback_data=f'register_{subdivision.id}_{message.message_thread_id}'))

    await message.answer(
        text=register_message.as_markdown(),
        reply_markup=keyboard.adjust(1).as_markup(),
        parse_mode=ParseMode.MARKDOWN)
    await message.delete()

@admin_group_router.callback_query(ChatTypeFilter(chat_type=['group', 'supergroup']), (F.data.startswith('register_')))
async def register_message_thread_id(callback_query: CallbackQuery, session):
    _, subdivision_id, message_thread_id = callback_query.data.split('_')
    message_thread_id = int(message_thread_id) if message_thread_id != 'None' else 0
    await upsert_subdivision_message_thread(session, int(subdivision_id), message_thread_id)
    await callback_query.message.delete()
    await callback_query.answer(text='Успешно зарегистрировано!', show_alert=True)

@admin_group_router.callback_query(ChatTypeFilter(chat_type=['group', 'supergroup']), (F.data.startswith('answer_')))
async def answering_inquiry(callback_query: CallbackQuery, session):
    user_id = callback_query.from_user.id
    personal_state = FSMContext()
    logger.warning(f'user_id = {user_id}')
    user = await get_user_data(session, user_id)
    chat_id = user.chat_id

    await callback_query.bot.send_message(chat_id=chat_id, text=f'callback_data={callback_query.data}')
    await callback_query.answer('Обращение отправлено в личный чат с ботом для редактирования', alert=True)
