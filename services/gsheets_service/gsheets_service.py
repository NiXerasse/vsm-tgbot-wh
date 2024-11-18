import asyncio

import gspread
from googleapiclient.discovery import build
from google.oauth2 import service_account

from services.gsheets_service.gsheets_raw_data_processor import GoogleRawDataProcessor

class GoogleSheetsService:

    def __init__(self, google_credentials_file, read_file_postfix):
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.creds = service_account.Credentials.from_service_account_file(google_credentials_file, scopes=self.scope)
        self.client = gspread.authorize(self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.sheets_service = build('sheets', 'v4', credentials=self.creds)
        self.read_file_postfix = read_file_postfix
        self.files_list = None

    def get_subdivision_from_file_name(self, file_name):
        return file_name.rstrip(self.read_file_postfix)

    def _file_filter(self, file):
        file_name = file['name']
        if file_name.startswith('.'):
            return False
        if not self.read_file_postfix and '.' in file_name:
            return False
        return file_name.endswith(self.read_file_postfix)

    def _update_files_list(self):
        query = "mimeType='application/vnd.google-apps.spreadsheet'"
        file_list = self.drive_service.files().list(q=query).execute().get('files', [])
        self.files_list = list(filter(self._file_filter, file_list))
        return self.files_list

    async def update_files_list(self):
        return await asyncio.get_running_loop().run_in_executor(None, self._update_files_list)

    def get_files_list(self):
        return self.files_list

    def open_sheet(self, file_name, worksheet_name='WorkedHours'):
        return self.client.open(file_name).worksheet(worksheet_name)

    async def async_open_sheet(self, file_name, worksheet_name='WorkedHours'):
        return await asyncio.get_running_loop().run_in_executor(
            None, self.open_sheet, file_name, worksheet_name)

    def _get_raw_worksheet_data(self, file, worksheet_name='WorkedHours'):
        result = self.sheets_service.spreadsheets().values().get(
            spreadsheetId=file['id'],
            range=worksheet_name,
            valueRenderOption='UNFORMATTED_VALUE'
        ).execute().get('values', [])
        return result

    def _get_structured_data_from_file(self, file):
        raw_data = self._get_raw_worksheet_data(file)
        struct_data = GoogleRawDataProcessor(raw_data).get_structured_worksheet_data()
        return struct_data

    @staticmethod
    def filter_structured_data(struct_data):
        for subdivision_data in struct_data.values():
            for tab_no, data in list(subdivision_data['data'].items()):
                if not tab_no or '-' not in tab_no or not data['ФИО']:
                    subdivision_data['data'].pop(tab_no)
        return struct_data

    def _get_structured_data(self):
        struct_data = {}
        for file in self.get_files_list():
            subdivision = file['name'].rstrip(self.read_file_postfix)
            struct_data[subdivision] = {
                'gsheets_id': file['id'],
                'data': self._get_structured_data_from_file(file)
            }
        filtered_data = GoogleSheetsService.filter_structured_data(struct_data)
        return filtered_data

    async def get_structured_data(self):
        return await asyncio.get_running_loop().run_in_executor(None, self._get_structured_data)
