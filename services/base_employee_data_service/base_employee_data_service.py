from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Employee
from repositories.employee_repository import EmployeeRepository


class BaseEmployeeDataService:
    employee_repo = EmployeeRepository()

    @staticmethod
    async def get_employee_by_tab_no(session: AsyncSession, tab_no: str) -> Employee:
        return await BaseEmployeeDataService.employee_repo.get_employee_by_tab_no(session, tab_no)
