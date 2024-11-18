from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Inquiry, Employee
from repositories.inquiry_repository import InquiryRepository


class InquiryService:
    inquiry_repo = InquiryRepository()

    @staticmethod
    async def get_not_hidden_inquiries_by_employee_tab_no(session: AsyncSession, tab_no: str):
        inquiries = await InquiryService.inquiry_repo.get_inquiries_by_employee_tab_no(session, tab_no)
        return [inquiry for inquiry in inquiries if 'hidden' not in inquiry.status]

    @staticmethod
    async def get_inquiry_with_messages_employee_subdivision_by_id(session, inquiry_id):
        return await InquiryService.inquiry_repo.get_inquiry_with_messages_employee_subdivision_by_id(
            session, inquiry_id)

    @staticmethod
    async def make_answered_enquiry_read(session: AsyncSession, inquiry: Inquiry):
        if inquiry.status == 'answered':
            await InquiryService.inquiry_repo.update_inquiry_status(session, inquiry, 'answered_and_read')

    @staticmethod
    async def get_inquiry_by_id(session: AsyncSession, inquiry_id: int):
        return await InquiryService.inquiry_repo.get_inquiry_by_id(session, inquiry_id)

    @staticmethod
    async def has_non_initiator_messages(session: AsyncSession, inquiry_id: int) -> bool:
        return await InquiryService.inquiry_repo.has_non_initiator_messages(session, inquiry_id)

    @staticmethod
    async def hide_inquiry_by_id(session: AsyncSession, inquiry_id: int):
        inquiry = await InquiryService.get_inquiry_by_id(session, inquiry_id)
        new_inquiry_status = inquiry.status + "_hidden"
        await InquiryService.inquiry_repo.update_inquiry_status(session, inquiry, new_inquiry_status)

    @staticmethod
    async def delete_inquiry_by_id(session, inquiry_id: int):
        await InquiryService.inquiry_repo.delete_inquiry_by_id(session, inquiry_id)

    @staticmethod
    async def add_message_to_inquiry(session, inquiry_id: int, message_text: str):
        await InquiryService.inquiry_repo.add_message_to_inquiry(session, inquiry_id, message_text)

    @staticmethod
    async def create_inquiry(session, employee: Employee, subdivision_id: int, inquiry_head: str, inquiry_body: str):
        return await InquiryService.inquiry_repo.create_inquiry(session, employee, subdivision_id, inquiry_head, inquiry_body)

    @staticmethod
    async def add_answer_to_inquiry(session: AsyncSession, inquiry_id: int, employee_id: int, answer: str):
        await InquiryService.inquiry_repo.add_answer_to_inquiry(session, inquiry_id, employee_id, answer)

    @staticmethod
    async def update_inquiry_status_by_id(session, inquiry_id: int, new_inquiry_status: str):
        await InquiryService.inquiry_repo.update_inquiry_status(session, inquiry_id, new_inquiry_status)
