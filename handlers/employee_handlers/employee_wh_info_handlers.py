from datetime import datetime

from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from babel.dates import get_month_names
from dateutil.relativedelta import relativedelta

from callback_data.employee_callback_data import DetailedWhInfoCallback, RateInfoCallback
from handlers.employee_handlers.employee_base_handlers import EmployeeBaseHandlers
from fsm.fsm_states.fsm_states import Authorised
from keyboards.common_keyboards import CommonKeyboards
from keyboards.employee_keyboards import EmployeeKeyboards
from utils.message_builders.employee_message_builder import EmployeeMessageBuilder
from utils.message_manager import MessageManager
from utils.util_data_types import MonthPeriod


class EmployeeWhInfoHandler(EmployeeBaseHandlers):

    @staticmethod
    @EmployeeBaseHandlers.router.callback_query(StateFilter(Authorised.start_menu), (F.data == 'get_wh_info'))
    async def choose_wh_info_period(callback_query: CallbackQuery, state: FSMContext, session, locale, _, tab_no):
        employee = await EmployeeBaseHandlers.employee_service.get_employee_by_tab_no(session, tab_no)

        now = datetime.now()
        current_month, current_year = now.month, now.year
        prev = now - relativedelta(months=1)
        prev_month, prev_year = prev.month, prev.year

        periods = [
            MonthPeriod(
                get_month_names(context='stand-alone', locale=locale)[prev_month], prev_month, prev_year
            ),
            MonthPeriod(
                get_month_names(context='stand-alone', locale=locale)[current_month], current_month, current_year
            ),
        ]

        await MessageManager.update_message(
            callback_query.message,
            EmployeeMessageBuilder.wh_main_info_message(employee, _),
            EmployeeKeyboards.get_wh_main_info_keyboard(periods, _)
        )

        await state.set_state(Authorised.wh_info_choose_period)

    @staticmethod
    @EmployeeBaseHandlers.router.callback_query(
        StateFilter(Authorised.wh_info_choose_period), DetailedWhInfoCallback.filter())
    async def wh_info(
            callback_query: CallbackQuery, callback_data: DetailedWhInfoCallback,
            state: FSMContext, session, _, tab_no):

        employee = await EmployeeBaseHandlers.employee_service.get_employee_by_tab_no(session, tab_no)

        target_period_start, target_period_end = EmployeeWhInfoHandler._get_target_period(
            callback_data.month, callback_data.year)

        wh_stats = await (EmployeeBaseHandlers
                          .employee_service.get_wh_statistics(session, tab_no, target_period_start, target_period_end))

        wh_info_message = EmployeeWhInfoHandler._generate_wh_info_message(
            employee, callback_data.month_str, callback_data.year, wh_stats, _)

        await MessageManager.update_message(
            callback_query.message, wh_info_message,
            EmployeeKeyboards.get_wh_info_keyboard(MonthPeriod(**vars(callback_data)), _)
        )

        await state.set_state(Authorised.wh_info)

    @staticmethod
    @EmployeeBaseHandlers.router.callback_query(StateFilter(Authorised.wh_info), RateInfoCallback.filter())
    async def get_rate_info(callback_query: CallbackQuery, state: FSMContext, _):
        await MessageManager.update_message(
            callback_query.message,
            EmployeeMessageBuilder.rate_info_message(_), CommonKeyboards.get_back_button_keyboard(_))
        await state.set_state(Authorised.rate_info)

    @staticmethod
    def _get_target_period(month: int, year: int):
        target_period_start = datetime(year, month, 1, 0, 0, 0)
        target_period_end = target_period_start + relativedelta(months=1)
        return target_period_start, target_period_end

    @staticmethod
    def _generate_wh_info_message(employee, target_month_str: str, target_year: int, wh_stats, _) -> str:
        wh_info_message = EmployeeMessageBuilder.wh_info_message(employee, target_month_str, target_year, _)
        wh_info_message += ''.join(EmployeeMessageBuilder.wh_info_subdivision(wh_stat, _) for wh_stat in wh_stats)
        return wh_info_message

    @staticmethod
    @EmployeeBaseHandlers.router.callback_query(StateFilter(Authorised.wh_info), DetailedWhInfoCallback.filter())
    async def send_detailed_wh_info(
            callback_query: CallbackQuery, callback_data: DetailedWhInfoCallback,
            state: FSMContext, session, _, tab_no, locale):

        await EmployeeWhInfoHandler._show_detailed_wh_info(
            callback_query, session, locale, tab_no, callback_data.month, callback_data.year, _)

        await callback_query.answer()
        await state.set_state(Authorised.wh_detailed_info)

    @staticmethod
    async def _show_detailed_wh_info(callback_query, session, locale, tab_no, month, year, _):
        png_image = await EmployeeBaseHandlers.employee_service.get_wh_detailed_info_img(
            session, tab_no, locale, month, year)
        if png_image is not None:
            await MessageManager.update_message(
                callback_query.message, '', CommonKeyboards.get_back_button_keyboard(_), new_photo=png_image)
        else:
            await MessageManager.update_message(
                callback_query.message, EmployeeMessageBuilder.no_time_records_message(_),
                CommonKeyboards.get_back_button_keyboard(_))
