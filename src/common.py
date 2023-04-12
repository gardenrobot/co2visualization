from datetime import datetime, date

from typing import TextIO


DATA_DIR = "../data/"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

def date_to_str(dte: date) -> str:
    return dte.strftime(DATE_FORMAT)

# TODO change names of converter functions
def to_str(dt: datetime) -> str:
    return dt.strftime(DATETIME_FORMAT)

def to_datetime(datetime_str: str) -> datetime:
    return datetime.strptime(datetime_str, DATETIME_FORMAT)

def round_to_5min(old_datetime: datetime) -> datetime:
    return old_datetime.replace(
        minute=int(old_datetime.minute/5)*5,
        second=0,
        microsecond=0,
    )

def write_header(f: TextIO) -> None:
    f.write("Datetime,Co2(PPM),Temp\n")
