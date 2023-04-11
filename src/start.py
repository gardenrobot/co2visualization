import os
import csv

from chartkick.flask import PieChart, LineChart
from datetime import datetime
from flask import render_template
from typing import Dict

from common import DATA_DIR
from flaskapp import app, celery
from tasks import sensorread


# TODO change the read interval into a cron
READ_INTERVAL = 300.0 # 5 minutes
CHART_TEMPLATE = "chart.template"


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(READ_INTERVAL, sensorread)


@app.route("/test")
def test():
    chart = PieChart({"Blueberry": 44, "Strawberry": 23})
    return render_template(CHART_TEMPLATE, chart=chart)


@app.route("/")
def linechart():
    print(os.path.dirname(os.path.realpath(__file__)))
    data = read_csv(datetime.now())
    chart = LineChart(data, xtitle="Time", ytitle="CO2 in ppm")
    return render_template(CHART_TEMPLATE, chart=chart)


def read_csv(date: datetime, existing_data={}) -> Dict[str, int]:
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
