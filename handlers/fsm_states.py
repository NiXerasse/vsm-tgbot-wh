from aiogram.fsm.state import StatesGroup, State


class Unauthorised(StatesGroup):
    start_menu = State()
    choosing_language = State()
    entering_pin = State()
    correct_pin_entered = State()
    entering_new_password = State()
    new_password_entered = State()
    entering_login = State()
    entering_password = State()
    password_entered = State()
    setting_password = State()

class Authorised(StatesGroup):
    start_menu = State()
    inquiry_menu = State()
    entering_inquiry_head = State()
    entered_inquiry_head = State()
    entering_inquiry_body = State()
    entered_inquiry_body = State()
    wh_info = State()
