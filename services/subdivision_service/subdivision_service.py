import os

from repositories.subdivision_repository import SubdivisionRepository


class SubdivisionService:
    admin_subdivision = os.getenv('ADMIN_SUBDIVISION')
    archive_subdivision = '.archive'
    service_subdivision = '.service'
    subdivision_repo = SubdivisionRepository()

    @staticmethod
    async def get_subdivisions(session):
        return await SubdivisionService.subdivision_repo.get_subdivisions(session)
