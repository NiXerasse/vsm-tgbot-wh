from aiohttp.web_routedef import static
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Inquiry, Employee, Message


class InquiryRepository:
    @staticmethod
    async def get_inquiry_with_messages_employee_subdivision_by_id(session: AsyncSession, inquiry_id: int):
        result = await session.execute(
            select(Inquiry)
            .options(
                selectinload(Inquiry.messages),
                selectinload(Inquiry.employee),
                selectinload(Inquiry.subdivision)
            )
            .where(Inquiry.id == inquiry_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_inquiry_status(session, inquiry, new_status):
        inquiry.status = new_status
        await session.commit()
        return inquiry

    @staticmethod
    async def get_inquiries_by_employee_tab_no(session: AsyncSession, tab_no: str):
        result = await session.execute(
            select(Inquiry)
            .join(Employee)
            .where(Employee.tab_no == tab_no)
        )
        return result.scalars().all()

    @staticmethod
    async def get_inquiry_by_id(session: AsyncSession, inquiry_id: int):
        result = await session.execute(
            select(Inquiry)
            .where(Inquiry.id == inquiry_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def has_non_initiator_messages(session: AsyncSession, inquiry_id: int) -> bool:
        stmt = (
            select(Message)
            .join(Inquiry, (Inquiry.id == inquiry_id) & (Inquiry.employee_id != Message.employee_id))
        )
        result = await session.execute(stmt)
        non_initiator_messages = result.scalars().first()

        return non_initiator_messages is not None

    @staticmethod
    async def delete_inquiry_by_id(session, inquiry_id: int):
        result = await session.execute(
            select(Inquiry).where(Inquiry.id == inquiry_id)
        )
        inquiry = result.scalar_one_or_none()

        if inquiry is None:
            raise ValueError(f"Inquiry with id {inquiry_id} not found")

        await session.delete(inquiry)
        await session.commit()

    @staticmethod
    async def add_message_to_inquiry(session, inquiry_id: int, message_text: str):
        inquiry = await InquiryRepository.get_inquiry_by_id(session, inquiry_id)

        new_message = Message(
            inquiry_id=inquiry.id, # type: ignore
            employee_id=inquiry.employee_id, # type: ignore
            content=message_text
        )
        session.add(new_message)

        inquiry.status = 'open'
        session.add(inquiry)

        await session.commit()

    @staticmethod
    async def create_inquiry(session, employee: Employee, subdivision_id: int, inquiry_head: str, inquiry_body: str):
        new_inquiry = Inquiry(
            employee_id=employee.id,
            subject=inquiry_head,
            status='open',
            subdivision_id=subdivision_id
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
        await session.refresh(new_inquiry, attribute_names=['messages', 'employee', 'subdivision'])

        return new_inquiry

    @staticmethod
    async def add_answer_to_inquiry(session: AsyncSession, inquiry_id: int, employee_id: int, answer: str):
        result = await session.execute(
            select(Inquiry)
            .where(Inquiry.id == inquiry_id)
        )
        inquiry = result.scalar_one_or_none()

        if inquiry is None:
            raise ValueError(f"Inquiry with id {inquiry_id} not found")

        new_message = Message(
            inquiry_id=inquiry_id,
            employee_id=employee_id,
            content=answer
        )

        session.add(new_message)

        inquiry.status = 'answered'
        session.add(inquiry)

        await session.commit()

    @staticmethod
    async def update_inquiry_status_by_id(session, inquiry_id: int, new_inquiry_status: str):
        await session.execute(
            update(Inquiry)
            .where(Inquiry.id ==inquiry_id)
            .values(status=new_inquiry_status)
        )
        await session.commit()
