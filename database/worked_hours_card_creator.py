import copy

import calendar
from datetime import datetime
from io import BytesIO

import cairosvg
from babel.dates import format_date, get_day_names

from lxml import etree

from locales.locales import gettext
from logger.logger import logger

svg_file_name = 'worked_hours.svg'

class WorkedHoursCardCreator:
    tree = None
    namespace = {"svg": "http://www.w3.org/2000/svg"}


    def __init__(self, locale='en'):
        if self.tree is None:
            self.tree = etree.parse(svg_file_name)

        self.svg_tree = copy.deepcopy(self.tree)
        self.root = self.svg_tree.getroot()
        self.locale = locale

    def set_value(self, element_id, value):
        element = self.root.find(f".//svg:text[@id='{element_id}']", namespaces=WorkedHoursCardCreator.namespace)
        tspan_element = element.find("svg:tspan", namespaces=WorkedHoursCardCreator.namespace)
        tspan_element.text = f'{value}'

    def set_values(self, element_id, values):
        element = self.root.find(f".//svg:text[@id='{element_id}']", namespaces=WorkedHoursCardCreator.namespace)
        tspan_elements = element.findall("svg:tspan", namespaces=WorkedHoursCardCreator.namespace)
        for tspan_element, value in zip(tspan_elements, values):
            tspan_element.text = f'{value}'

    def get_value(self, element_id):
        element = self.root.find(f".//svg:text[@id='{element_id}']", namespaces=WorkedHoursCardCreator.namespace)
        tspan_element = element.find("svg:tspan", namespaces=WorkedHoursCardCreator.namespace)
        return tspan_element.text

    def fill_days_and_hours(self, month, year, hours_worked):
        first_weekday, days_in_month = calendar.monthrange(year, month)
        day_numbers = [0] * first_weekday + [*range(1, days_in_month + 1)]
        day_numbers = day_numbers + [0] * (35 - len(day_numbers))
        for i, day in enumerate(day_numbers, start=1):
            self.set_value(f'day_{i}', day if day else '')
            wh = hours_worked.get(day, None)
            self.set_value(f'hours_{i}', f'{wh if wh else ''}')

    def fill_day_names(self):
        days_en = ['sun', 'mon', 'tue', 'wen', 'thu', 'fri', 'sat']
        days_loc = get_day_names('abbreviated', locale=self.locale).values()
        for day_en, day_loc in zip(days_en, days_loc):
            logger.warning(f'Setting {day_en} to {day_loc}')
            self.set_value(f'{day_en}', f'{day_loc}')

    def fill_footer(self, hours_worked):
        _ = gettext.get(self.locale, 'en')
        days_worked_text = f'{_('Number of days worked')}: {sum(h > 0 for h in hours_worked.values())}'
        hours_worked_text = f'{_('Accounted hours')}: {sum(hours_worked.values())}'
        self.set_values('footer', [days_worked_text, hours_worked_text])

    def generate_png_card(self, subdivision, full_name, tab_no, month, year, hours_worked=None):
        date = datetime(year, month, 1)
        month_name = format_date(date, "LLLL", locale=self.locale).capitalize()

        self.set_value('month_year', f'{month_name} {year}')
        self.set_values('employee', [subdivision, tab_no, full_name])
        self.fill_day_names()
        self.fill_days_and_hours(month, year, hours_worked)
        self.fill_footer(hours_worked)

        svg_xml = etree.tostring(self.root, xml_declaration=True, encoding='UTF-8')
        png_image = BytesIO()
        cairosvg.svg2png(bytestring=svg_xml, write_to=png_image, output_width=800, dpi=300)
        png_image.seek(0)

        return png_image.getvalue()
