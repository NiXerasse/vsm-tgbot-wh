# from aiogram.fsm.context import FSMContext
# from aiogram.types import Message
#
# from filters.is_admin import IsAdmin
#
#
# async def authorised_start(message: Message, state: FSMContext, session, _, tab_no):
#     if await IsAdmin()(message, state):
#         from handlers.admin import admin_start
#         await admin_start(message, state, session, _)
#     else:
#         from handlers.employee_handlers.employee_nav_handlers import EmployeeNavHandlers
#         await EmployeeNavHandlers.go_to_main_menu(message, state, session, _, tab_no)
