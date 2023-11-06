from celery import Celery, Task
from flaskapp import celery
from common import DATA_DIR, datetime_to_str, str_to_datetime, round_to_5min, write_header

import co2meter

import os
import csv


@celery.task()
def sensorread() -> None:
    """Get sensor data and log it to a file associated with the current date"""
    print("sensorread()")

    #create data/ dir if it does not exist
    if not os.path.isdir(DATA_DIR):
        os.mkdir(DATA_DIR)

    # Get data
    # TODO improve error messaging here
    try:
        data = list(co2meter.CO2monitor().read_data())
    except Exception as e:
        print(e)
        return
    for i in range(len(data)):
        data[i] = str(data[i])

    today = data[0].split(" ")[0]
    filepath = os.path.join(DATA_DIR, today) + ".csv"

    # round datetime down
    data[0] = datetime_to_str(round_to_5min(str_to_datetime(data[0])))

    # write csv header if it does not exist
    if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
        with open(filepath, "w") as f:
            write_header(f)

    # write data
    with open(filepath, "a") as f:
        csv_writer = csv.writer(f, delimiter=",")
        csv_writer.writerow(data)
