import random
from datetime import datetime

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract, text
from database.models import Employee, EmployeeAdmin, Inquiry, Subdivision, TimeRecord
from logger.logger import logger


class EmployeeRepository:
    CHUNK_SIZE = 1000

    @staticmethod
    async def get_employee_by_id(session: AsyncSession, employee_id: int):
        result = await session.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_employee_by_pin(session: AsyncSession, pin: str):
        result = await session.execute(
            select(Employee).where(Employee.pin == pin)
        )
        return result.scalars().first()

    @staticmethod
    async def get_employee_by_tab_no(session: AsyncSession, tab_no: str):
        result = await session.execute(
            select(Employee).where(Employee.tab_no == tab_no)
        )
        return result.scalars().first()

    @staticmethod
    async def is_employee_admin(session: AsyncSession, employee_id: int):
        result = (await session.execute(
            select(EmployeeAdmin)
            .where(EmployeeAdmin.employee_id == employee_id)
        )).scalar_one_or_none()
        return result is not None

    @staticmethod
    async def has_answered_inquiries(session: AsyncSession, employee_id: int) -> bool:
        result = await session.execute(
            select(Inquiry)
            .where(Inquiry.employee_id == employee_id, Inquiry.status == 'answered')
            .limit(1)
        )
        return result.scalar() is not None

    @staticmethod
    async def get_wh_statistics(session: AsyncSession, tab_no: str, start_date, end_date):
        stmt = (
            select(
                Subdivision.name,
                func.count().filter(TimeRecord.hours_worked > 0).label("count_nonzero"),
                func.sum(TimeRecord.hours_worked).label("sum_total")
            )
            .join(Employee, Employee.id == TimeRecord.employee_id)
            .join(Subdivision, Subdivision.id == TimeRecord.subdivision_id)
            .where(
                and_(
                    Employee.tab_no == tab_no,
                    TimeRecord.work_date >= start_date,
                    TimeRecord.work_date < end_date
                )
            )
            .group_by(Subdivision.name)
        )

        result = await session.execute(stmt)
        statistics = result.fetchall()

        return [
            {
                "subdivision_name": row.name,
                "count_nonzero": row.count_nonzero or 0,
                "sum_total": row.sum_total or 0
            }
            for row in statistics
        ]

    @staticmethod
    async def get_worked_hours_by_employee_tab_no(session: AsyncSession, tab_no: str, month: int, year: int):
        stmt = (
            select(Subdivision.name, Employee.full_name, TimeRecord.work_date, TimeRecord.hours_worked)
            .join(Employee, Employee.id == TimeRecord.employee_id)
            .join(Subdivision, Subdivision.id == TimeRecord.subdivision_id)
            .where(Employee.tab_no == tab_no)
            .where(extract('month', TimeRecord.work_date) == month)
            .where(extract('year', TimeRecord.work_date) == year)
            .order_by(Subdivision.name, TimeRecord.work_date)
        )
        result = await session.execute(stmt)

        subdivision_hours = {}
        for subdivision_name, employee_full_name, work_date, hours_worked in result.fetchall():
            day_of_month = work_date.day

            if subdivision_name not in subdivision_hours:
                subdivision_hours[subdivision_name] = {'employee_full_name': employee_full_name, 'hours_worked': {}}

            subdivision_hours[subdivision_name]['hours_worked'][day_of_month] = hours_worked

        return subdivision_hours

    @staticmethod
    async def get_subdivisions_by_employee_tab_no(session: AsyncSession, tab_no: str) -> list[Subdivision]:
        result = await session.execute(
            select(Subdivision)
            .join(TimeRecord, TimeRecord.subdivision_id == Subdivision.id)
            .join(Employee, Employee.id == TimeRecord.employee_id)
            .where(Employee.tab_no == tab_no)
        )

        subdivisions = result.scalars().all()
        return list(subdivisions)

    @staticmethod
    def generate_pass():
        length = 6
        allowed_chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ123456789'
        password = ''.join(random.choice(allowed_chars) for _ in range(length))
        return password

    @staticmethod
    async def upsert_employee(session: AsyncSession, tab_no: str, full_name: str):
        result = await session.execute(select(Employee).where(Employee.tab_no == tab_no))
        employee = result.scalar_one_or_none()

        if employee is None:
            logger.warning(f'Inserting new employee {tab_no}: {full_name}')
            employee = Employee(tab_no=tab_no, full_name=full_name, pin='')
            session.add(employee)
            while True:
                employee.pin = EmployeeRepository.generate_pass()
                try:
                    await session.commit()
                    return employee
                except IntegrityError as e:
                    if not("unique constraint" in str(e.orig) and "pin" in str(e.orig)):
                        raise e
        elif employee.full_name != full_name:
            employee.full_name = full_name
            await session.commit()

        return employee

    @staticmethod
    async def add_employee(session: AsyncSession, tab_no: str, full_name: str):
        employee = Employee(tab_no=tab_no, full_name=full_name, pin=EmployeeRepository.generate_pass())
        session.add(employee)
        await session.commit()
        await session.flush()
        return employee

    @staticmethod
    async def _upsert_time_record(
            session: AsyncSession,
            employee: Employee, subdivision: Subdivision, work_date: datetime, hours_worked: int, commit=True):
        await session.execute(
            pg_insert(TimeRecord).values(
                employee_id=employee.id,
                subdivision_id=subdivision.id,
                work_date=work_date,
                hours_worked=hours_worked
            ).on_conflict_do_update(
                index_elements=['employee_id', 'subdivision_id', 'work_date'],
                set_={'hours_worked': hours_worked}
            )
        )
        if commit:
            await session.commit()

    @staticmethod
    async def upsert_time_records(session: AsyncSession, time_records: [dict]):
        if time_records:
            for ptr in range(0, len(time_records), EmployeeRepository.CHUNK_SIZE):
                await session.execute(
                    pg_insert(TimeRecord)
                    .values(time_records[ptr:ptr + EmployeeRepository.CHUNK_SIZE])
                    .on_conflict_do_update(
                        index_elements=['employee_id', 'subdivision_id', 'work_date'],
                        set_={'hours_worked': text('excluded.hours_worked')}
                    )
                )

            await session.commit()

    @staticmethod
    async def prepare_time_records(employee: Employee, subdivision: Subdivision, date_worked_hours: dict):

        time_records = []
        current_month = datetime.now().month
        for work_date, hours_worked in date_worked_hours.items():
            if work_date.month < current_month - 1:
                logger.warning(f'Trying to add record on closed period: {employee.full_name} -> {work_date}')
                continue

            time_records.append({
                'employee_id': employee.id,
                'subdivision_id': subdivision.id,
                'work_date': work_date,
                'hours_worked': hours_worked
            })

        return time_records

    @staticmethod
    async def get_employees_by_tab_no(session: AsyncSession, tab_no_list: list[str]):
        result = await session.execute(
            select(Employee).where(Employee.tab_no.in_(tab_no_list))
        )
        return result.scalars().all()

    @staticmethod
    async def upsert_employee_admin(session: AsyncSession, employee: Employee):
        await session.execute(
            pg_insert(EmployeeAdmin).values(employee_id=employee.id)
            .on_conflict_do_nothing(index_elements=['employee_id'])
        )
        await session.commit()

    @staticmethod
    async def get_employee_admins(session: AsyncSession):
        result = await session.execute(
            select(EmployeeAdmin)
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_employees(session: AsyncSession):
        return (await session.execute(select(Employee))).scalars().all()

    @staticmethod
    async def reset_employee_password(session, employee_id):
        employee = await EmployeeRepository.get_employee_by_id(session, employee_id)
        employee.password = ''
        await session.commit()
        return employee

    @staticmethod
    async def get_all_time_records(session: AsyncSession):
        return (await session.execute(select(TimeRecord))).scalars().all()
