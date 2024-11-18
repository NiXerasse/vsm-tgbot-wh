from sqlalchemy.ext.asyncio import AsyncSession

from services.auth_service.auth_result import AuthResult
from services.auth_service.auth_status import AuthStatus
from services.base_employee_data_service.base_employee_data_service import BaseEmployeeDataService


class AuthService(BaseEmployeeDataService):

    @staticmethod
    async def authorize_employee_by_pin(session: AsyncSession, pin: str) -> AuthResult:
        employee = await AuthService.employee_repo.get_employee_by_pin(session, pin)
        if employee is None:
            return AuthResult(status=AuthStatus.NOT_FOUND)
        if employee.password:
            return AuthResult(status=AuthStatus.ALREADY_AUTHORIZED, employee=employee)
        return AuthResult(status=AuthStatus.SUCCESS, employee=employee)

    @staticmethod
    async def set_employee_password(session: AsyncSession, tab_no: str, password: str):
        employee = await AuthService.get_employee_by_tab_no(session, tab_no)
        employee.password = password
        session.add(employee)
        await session.commit()

    @staticmethod
    async def is_employee_admin(session: AsyncSession, employee_id: int) -> bool:
        return await AuthService.employee_repo.is_employee_admin(session, employee_id)
