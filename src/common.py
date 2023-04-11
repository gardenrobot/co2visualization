from datetime import datetime

from typing import TextIO


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


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

#def round_to_5min(datetime_str: str) -> str:
#    return to_str(round_to_5min(to_datetime(datetime_str)))

def write_header(f: TextIO) -> None:
    f.write("Datetime,Co2(PPM),Temp\n")
