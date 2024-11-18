from datetime import datetime, timedelta

from debug_tools.logging import log_context


class GoogleRawDataProcessor:
    REQ_FIELDS = {'Таб. №', 'ФИО'}

    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.struct_data = {}

    def get_structured_worksheet_data(self):
        header = GoogleRawDataProcessor._process_header(self.raw_data[0])

        for row in self.raw_data[1:]:
            data_record = GoogleRawDataProcessor._extract_data_record(row, header)
            if not GoogleRawDataProcessor._is_good_data_record(data_record):
                continue

            tab_no, full_name = data_record['Таб. №'], data_record['ФИО']
            self.struct_data.setdefault(tab_no, {'ФИО': full_name, 'data_records': {}})

            self._get_wh_data(data_record, tab_no)

        return self.struct_data

    @staticmethod
    def _process_header(header):
        return [
            GoogleRawDataProcessor.convert_serial_to_date(h) if isinstance(h, int) else h.strip()
            for h in header
        ]

    @staticmethod
    def _extract_data_record(row, header):
        return {
            h: (value.strip() if isinstance(value, str) else value)
            for h, value in zip(header, row)
        }

    @staticmethod
    def _is_good_data_record(data_record):
        return all(
            field in data_record
            for field in GoogleRawDataProcessor.REQ_FIELDS
        )

    def _get_wh_data(self, data_record, tab_no):
        wh_data = self.struct_data[tab_no]['data_records']
        for column, value in data_record.items():
            if not isinstance(column, str):
                wh_data[column] = wh_data.get(column, 0) + (value if isinstance(value, int) else 0)

    @staticmethod
    def convert_serial_to_date(serial_number):
        start_date = datetime(1899, 12, 30)
        return start_date + timedelta(days=serial_number)
