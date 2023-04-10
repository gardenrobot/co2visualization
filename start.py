import datetime
import os
import csv

from chartkick.flask import chartkick_blueprint
from chartkick.flask import PieChart, LineChart

from flask import Flask, render_template

from flask_celeryext import FlaskCeleryExt

from celery import Celery, Task

import co2meter as co2


READ_INTERVAL = 300.0 # 5 minutes
DATA_DIR = "data/"

app = Flask("testapp")
app.config.update(dict(
    CELERY_ALWAYS_EAGER=True,
    CELERY_RESULT_BACKEND="cache",
    CELERY_CACHE_BACKEND="memory",
    CELERY_EAGER_PROPAGATES=True),
    CELERY_BROKER_URL="redis://localhost",
)
app.register_blueprint(chartkick_blueprint)
ext = FlaskCeleryExt()
ext.init_app(app)
celery = ext.celery

@celery.task()
def sensorread():
    """Get sensor data and log it to a file associated with the current date"""
    #create data/ dir if it does not exist
    if not os.path.isdir(DATA_DIR):
        os.mkdir(DATA_DIR)

    # Get data
    data = list(co2.CO2monitor().read_data())
    for i in range(len(data)):
        data[i] = str(data[i])

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(DATA_DIR, today) + ".csv"

    # write csv header if it does not exist
    if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
        with open(filepath, "w") as f:
            f.write("datetime,co2,temp\n")

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
    return render_template("chart.template", chart=chart)

@app.route("/")
def linechart():
    data = read_csv(datetime.datetime.now())
    chart = LineChart(data, xtitle="Time", ytitle="CO2 in ppm")
    return render_template("chart.template", chart=chart)

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
