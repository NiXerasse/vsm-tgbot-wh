from datetime import timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import SubdivisionMessageThread, Subdivision, InquiryMessageMapping, Inquiry


class AdminGroupMessageRepository:
    @staticmethod
    async def get_message_thread_by_subdivision_id(session: AsyncSession, subdivision_id: int) -> int | None:
        result = await session.execute(
            select(SubdivisionMessageThread.message_thread_id)
            .where(SubdivisionMessageThread.subdivision_id == subdivision_id)
        )
        return result.scalar_one_or_none() or 0

    @staticmethod
    async def get_service_subdivision_id(session: AsyncSession, name: str):
        result = await session.execute(
            select(Subdivision.id)
            .where(Subdivision.name == name)
        )
        return result.scalar()

    @staticmethod
    async def get_inquiry_message_mapping(session: AsyncSession, inquiry_id: int):
        result = await session.execute(
            select(InquiryMessageMapping).where(InquiryMessageMapping.inquiry_id == inquiry_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def upsert_inquiry_message_mapping(
            session: AsyncSession, inquiry_id: int, message_id: int, message_thread_id: int):

        inquiry_message_mapping = InquiryMessageMapping(
            inquiry_id=inquiry_id,
            message_id=message_id,
            message_thread_id=message_thread_id
        )
        await session.merge(inquiry_message_mapping)
        await session.commit()

    @staticmethod
    async def delete_inquiry_message_mapping(session: AsyncSession, inq_mess_map: InquiryMessageMapping):
        await session.delete(inq_mess_map)
        await session.commit()

    @staticmethod
    async def upsert_subdivision_message_thread(session: AsyncSession, subdivision_id: int, message_thread_id: int):
        new_entry = SubdivisionMessageThread(
            subdivision_id=subdivision_id,
            message_thread_id=message_thread_id
        )
        await session.merge(new_entry)
        await session.commit()
        return new_entry

    @staticmethod
    async def get_expiring_admin_group_messages(session: AsyncSession, hours_older_than: int):
        time_threshold = func.now() - timedelta(hours=hours_older_than)

        result = await session.execute(
            select(InquiryMessageMapping, Subdivision.name, Inquiry)
            .join(SubdivisionMessageThread,
                  InquiryMessageMapping.message_thread_id == SubdivisionMessageThread.message_thread_id)
            .join(Subdivision, SubdivisionMessageThread.subdivision_id == Subdivision.id)
            .join(Inquiry, InquiryMessageMapping.inquiry_id == Inquiry.id)
            .where(InquiryMessageMapping.updated < time_threshold)
        )

        return result.all()
