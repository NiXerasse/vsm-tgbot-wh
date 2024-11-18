from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Subdivision
from services.base_employee_data_service.base_employee_data_service import BaseEmployeeDataService
from services.employee_service.worked_hours_card_creator import WorkedHoursCardCreator


class EmployeeService(BaseEmployeeDataService):
    @staticmethod
    async def has_answered_inquiries(session: AsyncSession, employee_id: int) -> bool:
        return await BaseEmployeeDataService.employee_repo.has_answered_inquiries(session, employee_id)

    @staticmethod
    async def get_wh_statistics(session: AsyncSession, tab_no: str, start_date, end_date):
        return await BaseEmployeeDataService.employee_repo.get_wh_statistics(session, tab_no, start_date, end_date)

    @staticmethod
    async def get_worked_hours_by_employee_tab_no(session: AsyncSession, tab_no: str, month: int, year: int):
        return await BaseEmployeeDataService.employee_repo.get_worked_hours_by_employee_tab_no(
            session, tab_no, month, year)

    @staticmethod
    async def get_subdivisions_by_employee_tab_no(session: AsyncSession, tab_no: str) -> list[Subdivision]:
        return await BaseEmployeeDataService.employee_repo.get_subdivisions_by_employee_tab_no(session, tab_no)

    @staticmethod
    async def get_wh_detailed_info_img(session: AsyncSession, tab_no: str, locale: str, month: int, year: int):
        wh_info = await EmployeeService.get_worked_hours_by_employee_tab_no(session, tab_no, month, year)
        subdivision_name, wh_data = next(iter(wh_info.items()))
        # It needs to be thought about representation of employee worked at different subdivisions during month

        return WorkedHoursCardCreator(locale).generate_png_card(
            subdivision=f'ОП "{subdivision_name}"',
            tab_no=tab_no,
            full_name=wh_data['employee_full_name'],
            month=month,
            year=year,
            hours_worked=wh_data['hours_worked'],
        )

    @staticmethod
    def format_tab_no(tab_no: str):
        return (tab_no.upper().
                replace('B', 'В').replace('C', 'С').
                replace('M', 'М').replace('K', 'К'))

    @staticmethod
    async def reset_employee_password(session, employee_id):
        return await BaseEmployeeDataService.employee_repo.reset_employee_password(session, employee_id)
