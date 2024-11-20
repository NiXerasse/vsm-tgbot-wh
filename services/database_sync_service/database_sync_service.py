from datetime import datetime
from pprint import pprint

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Employee, Subdivision, TimeRecord
from debug_tools.logging import log_context, async_log_context
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

    @staticmethod
    def _prepare_time_records(
            session: AsyncSession,
            employee: Employee, subdivision: Subdivision, date_worked_hours: dict, time_records: dict):

        current_month = datetime.now().month
        for work_date, hours_worked in date_worked_hours.items():
            if work_date.month < current_month - 1:
                logger.warning(f'Trying to add record on closed period: {employee.full_name} -> {work_date}')
                continue

            time_record = time_records.get((employee.id, subdivision.id, work_date.strftime('%x')), None)
            if time_record is None:
                time_record = TimeRecord(
                    employee_id=employee.id,
                    subdivision_id=subdivision.id,
                    work_date=work_date,
                    hours_worked=hours_worked
                )
                time_records[(employee.id, subdivision.id, work_date.strftime('%x'))] = time_record
                session.add(time_record)
            elif time_record.hours_worked != hours_worked:
                time_record.hours_worked = hours_worked


    async def _process_employee(self, session, tab_no, record, employees, subdivision, time_records):
        full_name = record['ФИО']
        if tab_no in employees:
            employee = employees[tab_no]
            if employee.full_name != full_name:
                employee.full_name = full_name
        else:
            employee = await self.employee_repo.add_employee(session, tab_no, full_name)
            employees[employee.tab_no] = employee

        self._prepare_time_records(session, employees[tab_no], subdivision, record['data_records'], time_records)

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
            async with async_log_context('reading employees'):
                employees = {
                    emp.tab_no: emp for emp in await self.employee_repo.get_all_employees(session)
                }
            async with async_log_context('reading time records'):
                time_records = {
                    (tr.employee_id, tr.subdivision_id, tr.work_date.strftime('%x')): tr
                    for tr in await self.employee_repo.get_all_time_records(session)
                }
            for subdivision_name in data:
                await self._process_subdivision(
                    session, subdivision_name, data[subdivision_name], employees, time_records)

            await session.commit()
