import random
from datetime import datetime

from sqlalchemy import select, and_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.engine import session_maker
from database.models import Subdivision, Employee, TimeRecord, User, Inquiry, Message, SubdivisionMessageThread, \
    InquiryMessageMapping
from logger.logger import logger


def generate_pass():
    length = 6
    allowed_chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ123456789'
    password = ''.join(random.choice(allowed_chars) for _ in range(length))
    return password

def format_tab_no(tab_no: str) -> str:
    return tab_no.upper().replace('B', 'В').replace('C', 'С').replace('M', 'М').replace('K', 'К')

async def add_subdivision(session: AsyncSession, name: str, gsheets_id: str):
    result = await session.execute(
        select(Subdivision).where(Subdivision.gsheets_id == gsheets_id)
    )
    subdivision_rec = result.scalars().first()
    if subdivision_rec is None:
        subdivision_rec = Subdivision(name=name, gsheets_id=gsheets_id)
        session.add(subdivision_rec)
        await session.commit()
        await session.refresh(subdivision_rec)
        logger.info(f'Added subdivision: \n{subdivision_rec}')
    elif subdivision_rec.name != name:
        subdivision_rec.name = name
        session.add(subdivision_rec)
        await session.commit()
        await session.refresh(subdivision_rec)
        logger.info(f'Updated subdivision: \n{subdivision_rec}')

    return subdivision_rec

async def update_employee_record(session: AsyncSession, e: Employee):
    is_added = False
    if not e.pin:
        e.pin = generate_pass()
    while not is_added:
        try:
            session.add(e)
            await session.commit()
            is_added = True
        except IntegrityError:
            e.pin = generate_pass()
            await session.rollback()
    await session.refresh(e)

async def add_employee(session: AsyncSession, tab_no: str, full_name: str):
    result = await session.execute(
        select(Employee).where(Employee.tab_no == tab_no)
    )
    employee_rec = result.scalars().first()
    if employee_rec is None:
        employee_rec = Employee(tab_no=tab_no, full_name=full_name)
        await update_employee_record(session, employee_rec)
        logger.info(f'Added employee: \n{employee_rec}')
    elif employee_rec.full_name != full_name:
        employee_rec.full_name = full_name
        await update_employee_record(session, employee_rec)
        logger.info(f'Updated employee: \n{employee_rec}')

    return employee_rec

async def add_time_records(
        session: AsyncSession, employee: Employee, subdivision: Subdivision, date_worked_hours: dict):
    to_log = ''
    for work_date in date_worked_hours:

        result = await session.execute(
            select(TimeRecord).where(
                TimeRecord.employee_id == employee.id,
                TimeRecord.subdivision_id == subdivision.id,
                TimeRecord.work_date == work_date
            )
        )
        time_record_rec = result.scalars().first()

        hours_worked = date_worked_hours[work_date]
        if time_record_rec is None:
            time_record_rec = TimeRecord(
                employee_id=employee.id,
                subdivision_id=subdivision.id,
                work_date=work_date,
                hours_worked=hours_worked
            )
            if work_date.month < datetime.now().month - 1:
                logger.warning(f'Trying to add record on closed period:\n{time_record_rec}')
            else:
                session.add(time_record_rec)
                to_log += f'Adding time record: \n{time_record_rec}\n'
        elif time_record_rec.hours_worked != hours_worked:
            if work_date.month < datetime.now().month - 1:
                logger.warning(f'Trying to update record on closed period:\n{time_record_rec}')
            else:
                time_record_rec.hours_worked = hours_worked
                session.add(time_record_rec)
                to_log += f'Updating time record: \n{time_record_rec}\n'

    await session.commit()
    if to_log:
        logger.info(f'Changed time records: \n{to_log}')

async def update_db(data):
    logger.info('Starting updating db from google sheets data')
    async with session_maker() as session:
        for subdivision_name in data:
            subdivision = await add_subdivision(session, subdivision_name, data[subdivision_name]['gsheets_id'])

            for tab_no, record in data[subdivision_name]['data_records'].items():
                full_name = record['ФИО']
                employee = await add_employee(session, tab_no, full_name)

                if employee:
                    await add_time_records(session, employee, subdivision, record['dates'])

    logger.info('Ended updating db from google sheets data')

async def get_employee(session: AsyncSession, tab_no: str):
    result = await session.execute(
        select(Employee).where(Employee.tab_no == tab_no)
    )
    return result.scalars().first()

async def add_user(session: AsyncSession, bot_id: int, user_id: int, chat_id: int):
    result = await session.execute(
        select(User).where(
            and_(
                User.bot_id == bot_id,
                User.user_id == user_id,
                User.chat_id == chat_id
            )
        )
    )
    user = result.scalars().first()
    if user is None:
        user = User(bot_id=bot_id,user_id=user_id, chat_id=chat_id)
        session.add(user)
        await session.commit()

    return user

async def get_employee_by_pin(session: AsyncSession, pin: str):
    result = await session.execute(
        select(Employee).where(Employee.pin == pin)
    )
    return result.scalars().first()

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

async def get_inquiries_by_employee_tab_no(session: AsyncSession, tab_no: str):
    result = await session.execute(
        select(Inquiry)
        .join(Employee)
        .where(Employee.tab_no == tab_no)
    )
    inquiries = result.scalars().all()
    return inquiries

async def get_inquiry_with_messages_by_id(session: AsyncSession, inquiry_id: int):
    result = await session.execute(
        select(Inquiry).options(selectinload(Inquiry.messages)).where(Inquiry.id == inquiry_id)
    )
    return result.scalar_one_or_none()

async def get_inquiry_by_id(session: AsyncSession, inquiry_id: int):
    result = await session.execute(
        select(Inquiry)
        .where(Inquiry.id == inquiry_id)
    )
    return result.scalar_one_or_none()

async def create_inquiry(session, tab_no: str, inquiry_head: str, inquiry_body: str):
    result = await session.execute(
        select(Employee).where(Employee.tab_no == tab_no)
    )
    employee = result.scalar_one_or_none()

    if employee is None:
        raise ValueError(f'Employee with tab_no {tab_no} not found')

    new_inquiry = Inquiry(
        employee_id=employee.id,
        subject=inquiry_head,
        status='open'
    )
    session.add(new_inquiry)
    await session.flush()

    new_message = Message(
        inquiry_id=new_inquiry.id,
        employee_id=employee.id,
        content=inquiry_body
    )
    session.add(new_message)

    await session.commit()
    return new_inquiry

async def delete_inquiry_by_id(session, inquiry_id: int):
    result = await session.execute(
        select(Inquiry).where(Inquiry.id == inquiry_id)
    )
    inquiry = result.scalar_one_or_none()

    if inquiry is None:
        raise ValueError(f"Inquiry with id {inquiry_id} not found")

    await session.delete(inquiry)
    await session.commit()

async def add_message_to_inquiry(session, inquiry_id: int, message_text: str):
    result = await session.execute(
        select(Inquiry).where(Inquiry.id == inquiry_id)
    )
    inquiry = result.scalar_one_or_none()

    if inquiry is None:
        raise ValueError(f"Inquiry with id {inquiry_id} not found")

    employee_id = inquiry.employee_id

    new_message = Message(
        inquiry_id=inquiry.id,
        employee_id=employee_id,
        content=message_text
    )

    session.add(new_message)

    inquiry.status = 'open'
    session.add(inquiry)

    await session.commit()

async def get_subdivisions(session):
    result = await session.execute(
        select(Subdivision)
    )
    return result.scalars().all()

async def upsert_subdivision_message_thread(session: AsyncSession, subdivision_id: int, message_thread_id: int):
    new_entry = SubdivisionMessageThread(
        subdivision_id=subdivision_id,
        message_thread_id=message_thread_id
    )
    await session.merge(new_entry)
    await session.commit()
    return new_entry

async def get_subdivisions_by_employee_tab_no(session: AsyncSession, tab_no: str) -> list[Subdivision]:
    result = await session.execute(
        select(Subdivision)
        .join(TimeRecord, TimeRecord.subdivision_id == Subdivision.id)
        .join(Employee, Employee.id == TimeRecord.employee_id)
        .where(Employee.tab_no == tab_no)
    )

    subdivisions = result.scalars().all()
    return list(subdivisions)

async def get_message_thread_by_subdivision_id(session: AsyncSession, subdivision_id: int) -> int | None:
    result = await session.execute(
        select(SubdivisionMessageThread.message_thread_id)
        .where(SubdivisionMessageThread.subdivision_id == subdivision_id)
    )

    return result.scalar()


async def upsert_inquiry_message_mapping(
        session: AsyncSession, inquiry_id: int, message_id: int, message_thread_id: int):
    inquiry_message_mapping = InquiryMessageMapping(
        inquiry_id=inquiry_id,
        message_id=message_id,
        subdivision_thread_id=message_thread_id
    )

    await session.merge(inquiry_message_mapping)
    await session.commit()
