# from aiogram.enums import ParseMode
# from aiogram.exceptions import TelegramBadRequest
# from aiogram.fsm.context import FSMContext
# from aiogram.types import Message, InputMediaPhoto, CallbackQuery, BufferedInputFile
# from aiogram import types
# from aiogram.utils.formatting import Text, Bold
#
# from config.env import vsm_logo_uri, admin_group_id
# from database.orm import get_inquiry_message_mapping, upsert_inquiry_message_mapping, \
#     get_message_thread_by_subdivision_id, get_service_sub_id, get_inquiry_by_id
# from keyboards.admin_group_inquiry_keyboards import AdminGroupInquiryKeyboards
# from locales.locales import gettext
# from logger.logger import logger
#
#
# async def update_start_message(
#         message: Message,
#         state: FSMContext,
#         caption: str,
#         markup: types.InlineKeyboardMarkup | None,
#         new_photo=None
# ):
#     start_msg_id = (await state.get_data()).get('start_msg_id')
#     media = vsm_logo_uri if new_photo is None else BufferedInputFile(new_photo, filename='image.png')
#     try:
#         await message.bot.edit_message_media(
#             media=InputMediaPhoto(
#                 media=media,
#                 caption=f'\u200B\n{caption}\n\u200B',
#                 parse_mode='MarkdownV2'
#             ),
#             chat_id=message.chat.id,
#             message_id=start_msg_id,
#             reply_markup=markup,
#         )
#     except TelegramBadRequest:
#         logger.warning('Trying to edit message while setting the same content')
#
# def update_callback_query_data(callback_query: CallbackQuery, data: str):
#     return CallbackQuery(
#         id=callback_query.id,
#         from_user=callback_query.from_user,
#         message=callback_query.message,
#         chat_instance=callback_query.chat_instance,
#         data=data
#     )
#
# def format_inquiry(inquiry, _ = gettext['ru']):
#     inquiry_message = Text(
#         Bold(inquiry.employee.full_name), '\n',
#         Bold(inquiry.employee.tab_no), '\n',
#         Bold(_('SD'), ' "', inquiry.subdivision.name, '"', '\n\n')
#     )
#
#     initiator = inquiry.employee_id
#
#     inquiry_message += Text(
#         Bold(_('Topic'), ': ', inquiry.subject), '\n',
#         '\n'
#     )
#
#     for msg in inquiry.messages:
#         icon = ' ❓ ' if msg.employee_id == initiator else ' ✅ '
#         inquiry_message += Text(
#             Bold(_('Date'), ': ', msg.sent_at.strftime('%d-%m-%y %H:%M')), '\n',
#             icon, msg.content, '\n\n'
#         )
#
#     return inquiry_message
#
# async def move_inquiry_to_thread(session, bot, inquiry_id, message_thread_id):
#     inq_mess_map = await get_inquiry_message_mapping(session, inquiry_id)
#     if inq_mess_map.message_thread_id == message_thread_id:
#         return
#
#     copied_message = await bot.copy_message(
#         chat_id=admin_group_id,
#         from_chat_id=admin_group_id,
#         message_id=inq_mess_map.message_id,
#         message_thread_id=message_thread_id,
#         reply_markup=AdminGroupInquiryKeyboards.get_inquiry_answer_keyboard(inquiry_id, gettext['ru'])
#     )
#
#     try:
#         await bot.delete_message(
#             chat_id=admin_group_id,
#             message_id=inq_mess_map.message_id,
#         )
#     except TelegramBadRequest:
#         logger.warning('Trying to delete old message...')
#
#     await upsert_inquiry_message_mapping(session, inq_mess_map.inquiry_id, copied_message.message_id, message_thread_id)
#
# async def move_inquiry_to_archive(session, bot, inquiry_id):
#     message_thread_id = await get_message_thread_by_subdivision_id(
#         session, (await get_service_sub_id(session, '.archive')))
#     await move_inquiry_to_thread(session, bot, inquiry_id, message_thread_id)
#
# async def move_inquiry_from_archive(session, bot, inquiry_id):
#     inquiry = await get_inquiry_by_id(session, inquiry_id)
#     message_thread_id = await get_message_thread_by_subdivision_id(session, inquiry.subdivision_id)
#     await move_inquiry_to_thread(session, bot, inquiry_id, message_thread_id)
#
# async def delete_inquiry_from_admin_group(session, bot, inquiry_id):
#     inq_mess_map = await get_inquiry_message_mapping(session, inquiry_id)
#     await bot.delete_message(
#         chat_id=admin_group_id,
#         message_id=inq_mess_map.message_id,
#     )
#     await session.delete(inq_mess_map)
#     await session.commit()
#
# async def update_inquiry_tg_message(session, bot, inquiry_with_messages):
#     inq_mess_map = await get_inquiry_message_mapping(session, inquiry_with_messages.id)
#
#     return await bot.edit_message_text(
#         chat_id=admin_group_id,
#         message_id=inq_mess_map.message_id,
#         text=format_inquiry(inquiry_with_messages).as_markdown(),
#         parse_mode=ParseMode.MARKDOWN_V2,
#         reply_markup=AdminGroupInquiryKeyboards.get_inquiry_answer_keyboard(inquiry_with_messages.id, gettext['ru'])
#     )
