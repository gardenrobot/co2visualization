from datetime import datetime, date

from typing import TextIO


DATA_DIR = "../data/"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


"""Functions for converting between datetime stuff."""
def date_to_str(dte: date) -> str:
    return dte.strftime(DATE_FORMAT)

def datetime_to_str(dt: datetime) -> str:
    return dt.strftime(DATETIME_FORMAT)

def str_to_datetime(datetime_str: str) -> datetime:
    return datetime.strptime(datetime_str, DATETIME_FORMAT)

def round_to_5min(old_datetime: datetime) -> datetime:
    """
    Take a datetime and return a similar one rounded down to the nearest 5
    minutes.
    """
    return old_datetime.replace(
        minute=int(old_datetime.minute/5)*5,
        second=0,
        microsecond=0,
    )

def write_header(f: TextIO) -> None:
    """Takes an open file and writers the csv header to it."""
    f.write("Datetime,Co2(PPM),Temp\n")
