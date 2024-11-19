from aiogram.fsm.state import StatesGroup, State


class AdminResetEmployeePassword(StatesGroup):
    entering_tab_no = State()
    entered_tab_no = State()
    wrong_tab_no = State()
    password_was_reset = State()
