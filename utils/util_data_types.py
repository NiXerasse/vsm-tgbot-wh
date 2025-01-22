from dataclasses import dataclass


@dataclass
class MonthPeriod:
    month_str: str
    month: int
    year: int
