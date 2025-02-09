import asyncio
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Employee, Subdivision, TimeRecord
from debug_tools.logging import async_log_context
from logger.logger import logger
from repositories.employee_repository import EmployeeRepository
from repositories.subdivision_repository import SubdivisionRepository
from repositories.user_repository import UserRepository
from services.subdivision_service.subdivision_service import SubdivisionService


class DatabaseSyncService:

    def __init__(self, session_maker):
        self.employee_cache = None
        self.time_record_cache = None
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

    async def _sync_admins(self, session: AsyncSession, subdivision_data: dict, employees):
        for tab_no, record in subdivision_data.items():
            employee = await self.employee_repo.get_employee_by_tab_no(session, tab_no)
            if employee is None:
                employee = await self.employee_repo.add_employee(session, tab_no, record['ФИО'])
                employees[tab_no] = employee
                await session.flush()

            await self.employee_repo.upsert_employee_admin(session, employee)

        await self._delete_old_admins(session, list(subdivision_data.keys()))

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
                    work_date=work_date.date(),
                    hours_worked=hours_worked
                )
                time_records[(employee.id, subdivision.id, work_date.strftime('%x'))] = time_record
                session.add(time_record)
            elif time_record.hours_worked != hours_worked:
                time_record.hours_worked = hours_worked
                session.add(time_record)


    async def _process_employee(self, session, tab_no, record, employees, subdivision, time_records):
        full_name = record['ФИО']
        if tab_no in employees:
            employee = employees[tab_no]
            if employee.full_name != full_name:
                employee.full_name = full_name
            session.add(employee)
        else:
            employee = await self.employee_repo.add_employee(session, tab_no, full_name)
            employees[employee.tab_no] = employee

        self._prepare_time_records(session, employees[tab_no], subdivision, record['data_records'], time_records)

    async def _process_subdivision(self, session, subdivision_name, subdivision_data, employees, time_records):
        logger.info(f'Updating {subdivision_name}: {len(subdivision_data['data'])} records')
        subdivision = await self.subdivision_repo.upsert_subdivision_and_gsheet(
            session, subdivision_name, subdivision_data['gsheets_id'])

        if subdivision_name == SubdivisionService.admin_subdivision:
            await self._sync_admins(session, subdivision_data['data'], employees)
            return

        for tab_no, record in subdivision_data['data'].items():
            await self._process_employee(session, tab_no, record, employees, subdivision, time_records)
            await asyncio.sleep(0) # Increase responsiveness


    async def _read_cache(self, session):
        if self.employee_cache is None:
            self.employee_cache = {
                    emp.tab_no: emp for emp in await self.employee_repo.get_all_employees(session)
                }
        if self.time_record_cache is None:
            self.time_record_cache = {
                    (tr.employee_id, tr.subdivision_id, tr.work_date.strftime('%x')): tr
                    for tr in await self.employee_repo.get_all_time_records(session)
                }
        return self.employee_cache, self.time_record_cache

    async def sync_db(self, data):
        async with self.session_maker() as session:
            async with async_log_context('reading employees and time records data'):
                employees, time_records = await self._read_cache(session)

            for subdivision_name in data:
                await self._process_subdivision(
                    session, subdivision_name, data[subdivision_name], employees, time_records)

            await session.commit()
