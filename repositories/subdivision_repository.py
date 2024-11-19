from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Subdivision, SubdivisionGSheet
from logger.logger import logger


class SubdivisionRepository:
    @staticmethod
    async def get_subdivisions(session: AsyncSession):
        result = await session.execute(
            select(Subdivision)
        )
        return result.scalars().all()

    @staticmethod
    async def _add_subdivision_and_gsheet(session: AsyncSession, subdivision_name: str, gsheets_id: str):
        new_subdivision = Subdivision(name=subdivision_name)
        session.add(new_subdivision)
        await session.flush()

        new_gsheet = SubdivisionGSheet(subdivision_id=new_subdivision.id, gsheets_id=gsheets_id)
        session.add(new_gsheet)
        await session.commit()

        return new_subdivision, new_gsheet

    @staticmethod
    async def _update_subdivision(session: AsyncSession, subdivision: Subdivision, subdivision_name: str):
        subdivision.name = subdivision_name
        session.add(subdivision)
        await session.commit()

    @staticmethod
    async def upsert_subdivision_and_gsheet(session: AsyncSession, subdivision_name: str, gsheets_id: str):
        result = await session.execute(
            select(SubdivisionGSheet).where(SubdivisionGSheet.gsheets_id == gsheets_id)
        )
        subdivision_gsheet = result.scalar_one_or_none()

        if subdivision_gsheet is None:
            subdivision, __ = \
                await SubdivisionRepository._add_subdivision_and_gsheet(session, subdivision_name, gsheets_id)
            logger.info(f'Added subdivision: {subdivision_name}')
        else:
            subdivision = (await session.execute(
                select(Subdivision).where(Subdivision.id == subdivision_gsheet.subdivision_id)
            )).scalar_one_or_none()

            if subdivision.name != subdivision_name:
                await SubdivisionRepository._update_subdivision(session, subdivision, subdivision_name)
                logger.info(f'Updated subdivision: {subdivision_name}')

        return subdivision
