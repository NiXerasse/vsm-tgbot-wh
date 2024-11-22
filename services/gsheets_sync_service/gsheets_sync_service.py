import asyncio

from gspread import Cell

from logger.logger import logger
from repositories.employee_repository import EmployeeRepository
from services.gsheets_service.gsheets_service import GoogleSheetsService


class GsheetsSyncService:
    def __init__(self, session_maker, gsheets_service: GoogleSheetsService):
        self.session_maker = session_maker
        self.gsheets_service = gsheets_service
        self.employee_repo = EmployeeRepository()

    @staticmethod
    async def _get_sheet_values(worksheet):
        return await asyncio.get_event_loop().run_in_executor(None, worksheet.get_all_values)

    async def _get_cells_to_update(self, session, ws_values):
        header, *rows = ws_values
        fio_col, tab_no_col, pass_col = [header.index(h) for h in ('ФИО', 'Таб. №', 'Пароль')]

        cells_to_update = []
        for row_no, row in enumerate(rows, start=2):
            fio, tab_no = row[fio_col].strip(), row[tab_no_col].strip()
            if not row or not fio or not tab_no or '-' not in tab_no:
                continue

            employee = await self.employee_repo.get_employee_by_tab_no(session, tab_no)
            if not employee:
                continue

            gsheets_pass = '*CHANGED*' if employee.password else employee.pin
            if row[pass_col] != gsheets_pass:
                logger.info(f'Pin for {employee.full_name} {employee.tab_no} is to be updated for {gsheets_pass}')
                cells_to_update.append(Cell(row=row_no, col=pass_col + 1, value=gsheets_pass))

        return cells_to_update

    async def gsheets_sync(self):
        files = await asyncio.get_running_loop().run_in_executor(None, self.gsheets_service.get_files_list)

        async with self.session_maker() as session:
            for file in files:
                subdivision = self.gsheets_service.get_subdivision_from_file_name(file['name'])
                logger.info(f'Updating worksheet data for {subdivision}')

                ws = await self.gsheets_service.async_open_sheet(file['name'])

                cells_to_update = await self._get_cells_to_update(
                    session, await GsheetsSyncService._get_sheet_values(ws))
                if cells_to_update:
                    await asyncio.get_running_loop().run_in_executor(
                        None, ws.update_cells, cells_to_update)
