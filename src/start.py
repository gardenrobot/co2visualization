import datetime
import os
import csv

from chartkick.flask import chartkick_blueprint
from chartkick.flask import PieChart, LineChart

from flask import Flask, render_template, Blueprint

from flask_celeryext import FlaskCeleryExt

from celery import Celery, Task

import co2meter as co2

from common import write_header, round_to_5min, to_str, to_datetime

from pprint import pprint


# TODO change the read interval into a cron
READ_INTERVAL = 10#300.0 # 5 minutes
DATA_DIR = "../data/"
CHART_TEMPLATE = "chart.template"

app = Flask("testapp")
app.config.update(dict(
    CELERY_ALWAYS_EAGER=True,
    CELERY_RESULT_BACKEND="cache",
    CELERY_CACHE_BACKEND="memory",
    CELERY_EAGER_PROPAGATES=True),
    CELERY_BROKER_URL="redis://localhost",
)
app.register_blueprint(chartkick_blueprint, template_folder='templates/')
ext = FlaskCeleryExt()
ext.init_app(app)
celery = ext.celery


@celery.task()
def sensorread():
    """Get sensor data and log it to a file associated with the current date"""
    print("sensorread()")

    #create data/ dir if it does not exist
    if not os.path.isdir(DATA_DIR):
        os.mkdir(DATA_DIR)

    # Get data
    data = list(co2.CO2monitor().read_data())
    for i in range(len(data)):
        data[i] = str(data[i])

    today = data[0].split(" ")[0]
    filepath = os.path.join(DATA_DIR, today) + ".csv"

    # round datetime down
    data[0] = to_str(round_to_5min(to_datetime(data[0])))

    # TODO do not write if datetime already exists in file

    # write csv header if it does not exist
    if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
        with open(filepath, "w") as f:
            write_header(f)

    # write data
    with open(filepath, "a") as f:
        csv_writer = csv.writer(f, delimiter=",")
        csv_writer.writerow(data)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(READ_INTERVAL, sensorread)

celery.conf.beat_schedule = {
    "sensorread": {
        "task": "sensorread",
        "schedule": READ_INTERVAL,
    }
}

@app.route("/test")
def test():
    chart = PieChart({"Blueberry": 44, "Strawberry": 23})
    return render_template(CHART_TEMPLATE, chart=chart)

@app.route("/")
def linechart():
    print(os.path.dirname(os.path.realpath(__file__)))
    data = read_csv(datetime.datetime.now())
    chart = LineChart(data, xtitle="Time", ytitle="CO2 in ppm")
    return render_template(CHART_TEMPLATE, chart=chart)

def read_csv(date, existing_data={}):
    """
    Takes a date and returns data from that date. Data is appended to
    existing_data.
    """
    date_str = date.strftime("%Y-%m-%d")
    with open(os.path.join(DATA_DIR, date_str+".csv")) as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for counter, row in enumerate(reader):
            if counter == 0:
                continue
            existing_data[row[0]] = int(row[1])
    return existing_data
