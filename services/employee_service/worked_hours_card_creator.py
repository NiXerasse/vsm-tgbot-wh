import copy

import calendar
import os
from datetime import datetime
from io import BytesIO

import cairosvg
from babel.dates import format_date, get_day_names

from lxml import etree

from locales.locales import gettext
from logger.logger import logger

svg_file_name = os.path.join(os.path.dirname(__file__), 'worked_hours.svg')
svg42_file_name = os.path.join(os.path.dirname(__file__), 'worked_hours_42.svg')

class WorkedHoursCardCreator:
    tree_35 = None
    tree_42 = None
    namespace = {"svg": "http://www.w3.org/2000/svg"}


    def __init__(self, month, year, locale='en'):
        if WorkedHoursCardCreator.tree_35 is None:
            logger.warning('Reading svg disk file')
            WorkedHoursCardCreator.tree_35 = etree.parse(svg_file_name)
            WorkedHoursCardCreator.tree_42 = etree.parse(svg42_file_name)

        self.month = month
        self.year = year
        self.first_weekday, self.days_in_month = calendar.monthrange(self.year, self.month)
        self.card_size = 35
        if self.first_weekday + self.days_in_month > self.card_size:
            self.card_size += 7

        self.svg_tree = copy.deepcopy(
            WorkedHoursCardCreator.tree_35 if self.card_size == 35 else WorkedHoursCardCreator.tree_42)
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

    def fill_days_and_hours(self, hours_worked):
        day_numbers = [0] * self.first_weekday + [*range(1, self.days_in_month + 1)]
        day_numbers = day_numbers + [0] * (self.card_size - len(day_numbers))
        for i, day in enumerate(day_numbers, start=1):
            self.set_value(f'day_{i}', day or '')
            wh = hours_worked.get(day, None)
            self.set_value(f'hours_{i}', f'{wh or ''}')

    def fill_day_names(self):
        days_en = ['sun', 'mon', 'tue', 'wen', 'thu', 'fri', 'sat']
        days_loc = get_day_names('abbreviated', locale=self.locale).values()
        for day_en, day_loc in zip(days_en, days_loc):
            self.set_value(f'{day_en}', f'{day_loc}')

    def fill_footer(self, hours_worked):
        _ = gettext.get(self.locale, 'en')
        days_worked_text = f'{_('Number of days worked')}: {sum(h > 0 for h in hours_worked.values())}'
        hours_worked_text = f'{_('Accounted hours')}: {sum(hours_worked.values())}'
        self.set_values('footer', [days_worked_text, hours_worked_text])

    def generate_png_card(self, subdivision, full_name, tab_no, hours_worked=None):
        date = datetime(self.year, self.month, 1)
        month_name = format_date(date, "LLLL", locale=self.locale).capitalize()

        self.set_value('month_year', f'{month_name} {self.year}')
        self.set_values('employee', [subdivision, tab_no, full_name])
        self.fill_day_names()
        self.fill_days_and_hours(hours_worked)
        self.fill_footer(hours_worked)

        svg_xml = etree.tostring(self.root, xml_declaration=True, encoding='UTF-8')
        png_image = BytesIO()
        cairosvg.svg2png(bytestring=svg_xml, write_to=png_image, output_width=800, dpi=300)
        png_image.seek(0)

        return png_image.getvalue()
