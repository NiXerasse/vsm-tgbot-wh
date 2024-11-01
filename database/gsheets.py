import pprint
from datetime import datetime, timedelta

import gspread
from gspread import Cell

from config.env import read_file_postfix
from database.engine import session_maker
from database.models import Employee
from database.orm import get_employee
from logger.logger import logger
import asyncio

from googleapiclient.discovery import build
from google.oauth2 import service_account


scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_file('vsmtgbot.json', scopes=scope)
drive_service = build('drive', 'v3', credentials=creds)
sheets_service = build('sheets', 'v4', credentials=creds)
client = gspread.authorize(creds)

def convert_serial_to_date(serial_number):
    start_date = datetime(1899, 12, 30)
    return start_date + timedelta(days=serial_number)

REQ_FIELDS = {'Таб. №', 'ФИО'}

def filter_incorrect_data(raw_data):
    for subdivision_data in raw_data.values():
        for tab_no, data in list(subdivision_data['data_records'].items()):
            if not tab_no or '-' not in tab_no or not data['ФИО']:
                subdivision_data['data_records'].pop(tab_no)
    return raw_data

def read_google_sheets_data():
    logger.info('Started reading google sheets data')

    query = "mimeType='application/vnd.google-apps.spreadsheet'"
    files = drive_service.files().list(q=query).execute().get('files', [])

    data = {}
    for file in files:
        if file['name'].startswith('.') or not file['name'].endswith(read_file_postfix):
            continue

        subdivision = file['name']
        data_records = {}
        data[subdivision] = {'gsheets_id': file['id'], 'data_records': data_records}

        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=file['id'],
            range='WorkedHours',
            valueRenderOption='UNFORMATTED_VALUE'
        ).execute().get('values', [])

        logger.info(f'Number of records for {subdivision}: {len(result) - 1}')
        header = result[0]

        for record in result[1:]:
            rec_with_hd = {h: (value.strip() if isinstance(value, str) else value) for h, value in zip(header, record)}
            if any(map(lambda h: h not in rec_with_hd, REQ_FIELDS)):
                continue
            if rec_with_hd['Таб. №'] not in data_records:
                data_records[rec_with_hd['Таб. №']] = {'ФИО': rec_with_hd['ФИО'], 'dates': {}}

            wh_data = data_records[rec_with_hd['Таб. №']]['dates']
            for h, value in zip(header, record):
                if isinstance(h, int):
                    wh_date = convert_serial_to_date(h)
                    wh_data[wh_date] = wh_data.get(wh_date, 0) + (value if isinstance(value, int) else 0)
            data_records[rec_with_hd['Таб. №']]['dates'] = wh_data

    logger.info('Finished reading google sheets data')
    return filter_incorrect_data(data)

async def read_google_sheets_data_async():
    return await asyncio.get_running_loop().run_in_executor(None, read_google_sheets_data)

async def update_google_sheets_data_async():
    def gdrive_get_files_list(ds):
        query = "mimeType='application/vnd.google-apps.spreadsheet'"
        return ds.files().list(q=query).execute().get('files', [])
    def open_gsheet(cl, subdiv, name):
        return cl.open(subdiv).worksheet(name)
    def get_all_values(w):
        return w.get_all_values()
    def update_cells(w, cells):
        if cells:
            w.update_cells(cells)

    logger.info('Started updating google sheets data')
    files = await asyncio.get_running_loop().run_in_executor(None, gdrive_get_files_list, drive_service)

    async with session_maker() as session:
        for file in files:
            if file['name'].startswith('.') or not file['name'].endswith(read_file_postfix):
                continue

            subdivision = file['name']

            ws = await asyncio.get_running_loop().run_in_executor(None, open_gsheet, client, subdivision, 'WorkedHours')
            header, *rows = await asyncio.get_running_loop().run_in_executor(None, get_all_values, ws)

            fio_col = header.index('ФИО')
            tab_no_col = header.index('Таб. №')
            pass_col = header.index('Пароль')

            cells_to_update = []
            for row_no, row in enumerate(rows, start=2):
                fio, tab_no = row[fio_col].strip(), row[tab_no_col].strip()
                if not row or not fio or not tab_no or '-' not in tab_no:
                    continue

                employee: Employee = await get_employee(session, tab_no)

                gsheets_pass = ''
                if employee:
                    if employee.password:
                        gsheets_pass = '*CHANGED*'
                    else:
                        gsheets_pass = employee.pin

                if row[pass_col] != gsheets_pass:
                    logger.info(f'Pin for {employee.full_name} {employee.tab_no} is to be updated for {employee.pin}')
                    cells_to_update.append(Cell(row=row_no, col=pass_col + 1, value=gsheets_pass))

            logger.info(f'Started updating worksheet data for {subdivision}')
            await asyncio.get_running_loop().run_in_executor(None, update_cells, ws, cells_to_update)
            logger.info(f'Updated worksheet data for {subdivision}')

    logger.info('Finished updating google sheets data')
