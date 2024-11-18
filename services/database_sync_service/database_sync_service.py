from sqlalchemy.ext.asyncio import AsyncSession

from logger.logger import logger
from repositories.employee_repository import EmployeeRepository
from repositories.subdivision_repository import SubdivisionRepository
from repositories.user_repository import UserRepository
from services.subdivision_service.subdivision_service import SubdivisionService


class DatabaseSyncService:

    def __init__(self, session_maker):
        self.session_maker = session_maker
        self.subdivision_repo = SubdivisionRepository()
        self.employee_repo = EmployeeRepository()
        self.user_repo = UserRepository()

    async def _delete_old_admins(self, session: AsyncSession, tab_nos: [str]):
        for admin in await self.employee_repo.get_employee_admins(session):
            employee = await self.employee_repo.get_employee_by_id(session, admin.employee_id)
            if employee.tab_no not in tab_nos:
                await self.user_repo.delete_user_with_tab_no(session, employee.tab_no)
                await session.delete(admin)
        await session.commit()

    async def _sync_admins(self, session: AsyncSession, tab_nos: [str]):
        employees = await self.employee_repo.get_employees_by_tab_no(session, tab_nos)
        for employee in employees:
            await self.employee_repo.upsert_employee_admin(session, employee)
        await session.commit()

        await self._delete_old_admins(session, tab_nos)

    async def _load_employee_cache(self, session: AsyncSession):
        return {
            emp.tab_no: emp for emp in await self.employee_repo.get_all_employees(session)
        }

    async def _process_employee(self, session, tab_no, record, employees, subdivision, time_records):
        full_name = record['ФИО']
        if tab_no in employees:
            employee = employees[tab_no]
            if employee.full_name != full_name:
                employee.full_name = full_name
        else:
            employee = await self.employee_repo.add_employee(session, tab_no, full_name, commit=False)
            employees[employee.tab_no] = employee

        records = await self.employee_repo.prepare_time_records(employee, subdivision, record['data_records'])
        time_records.extend(records)

    async def _process_subdivision(self, session, subdivision_name, subdivision_data, employees, time_records):
        logger.info(f'Updating {subdivision_name}: {len(subdivision_data['data'])} records')
        subdivision = await self.subdivision_repo.upsert_subdivision_and_gsheet(
            session, subdivision_name, subdivision_data['gsheets_id'])

        for tab_no, record in subdivision_data['data'].items():
            await self._process_employee(session, tab_no, record, employees, subdivision, time_records)

        if subdivision_name == SubdivisionService.admin_subdivision:
            tab_nos = list(subdivision_data['data'].keys())
            await self._sync_admins(session, tab_nos)

    async def sync_db(self, data):
        async with self.session_maker() as session:
            employees = {
                emp.tab_no: emp for emp in await self.employee_repo.get_all_employees(session)
            }

            time_records = []
            for subdivision_name in data:
                await self._process_subdivision(
                    session, subdivision_name, data[subdivision_name], employees, time_records)

            await self.employee_repo.upsert_time_records(session, time_records)

            await session.commit()
