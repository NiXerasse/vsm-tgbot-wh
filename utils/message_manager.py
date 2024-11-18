from aiogram import types, Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, InputMediaPhoto

from config.env import vsm_logo_uri
from logger.logger import logger


class MessageManager:
    @staticmethod
    async def update_main_message(
            initiator_message: types.Message, state: FSMContext,
            start_msg_id: int | None, caption='', keyboard=None):

        start_msg = await initiator_message.answer_photo(
            caption=f'\u200C\n{caption}\n\u200C',
            photo=vsm_logo_uri,
            reply_markup=keyboard,
            parse_mode='MarkdownV2',
        )

        if start_msg_id is not None:
            try:
                await initiator_message.bot.delete_message(chat_id=initiator_message.chat.id, message_id=start_msg_id)
            except TelegramBadRequest:
                ...

        if initiator_message:
            await initiator_message.delete()
        await state.update_data({'start_msg_id': start_msg.message_id})

    @staticmethod
    async def update_main_message_from_outer_space(bot: Bot, user_id: int, start_msg_id: int | None, caption='', keyboard=None):
        if start_msg_id is not None:
            try:
                await bot.delete_message(chat_id=user_id, message_id=start_msg_id)
            except TelegramBadRequest:
                ...

        start_msg = await bot.send_photo(
            chat_id=user_id,
            photo=vsm_logo_uri,
            caption=f'\u200C\n{caption}\n\u200C',
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=keyboard
        )

        return start_msg

    @staticmethod
    async def update_message(
        message: types.Message, caption: str,
        markup: types.InlineKeyboardMarkup | None, new_photo=None
    ):
        media = vsm_logo_uri if new_photo is None else BufferedInputFile(new_photo, filename='image.png')
        try:
            await message.edit_media(
                media=InputMediaPhoto(
                    media=media,
                    caption=f'\u200C\n{caption}\n\u200C',
                    parse_mode='MarkdownV2'
                ),
                reply_markup=markup,
            )
        except TelegramBadRequest:
            logger.warning('Trying to edit message while setting the same content')

    @staticmethod
    async def answer_message_and_delete(message, answer, keyboard):
        await message.answer(
            text=answer,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN_V2)
        await message.delete()

    @staticmethod
    async def delete_callback_message_and_alert(callback_query, popup):
        await callback_query.message.delete()
        await callback_query.answer(text=popup, show_alert=True)
