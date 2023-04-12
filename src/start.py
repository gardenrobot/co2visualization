import os
import csv

from chartkick.flask import PieChart, LineChart
from datetime import datetime, date, timedelta
from flask import render_template
from typing import Dict, List

from common import to_str, date_to_str, DATA_DIR
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
    data = read_csv(datetime.now())
    chart = LineChart(data, xtitle="Time", ytitle="CO2 in ppm")
    return render_template(CHART_TEMPLATE, chart=chart)


@app.route("/7dayoverlap")
def overlap():

    data = [{
        "name": "baseline",
        "data": create_baseline(),
        "color": "#ffffff",
    }]

    all_days = date_range(datetime.today(), 7)
    for day in all_days:
        csv_data = read_csv(day)
        daily_data = {}
        for row_datetime, co2 in csv_data.items():
            time_str = row_datetime.split(" ")[1]
            daily_data[time_str] = co2
        data.append({
            "name": date_to_str(day),
            "data": daily_data,
        })

    chart = LineChart(data, xtitle="Time", ytitle="CO2 in ppm")
    return render_template(CHART_TEMPLATE, chart=chart)


def create_baseline() -> Dict[str, int]:
    """
    Return a dummy dataset with every 5minute interval filled.
    This is a hack. Include this as the first dataset when rendering multiple
    lines to avoid a rendering error.
    """
    data = {}
    for hour in range(24):
        if hour < 10:
            hour = "0"+str(hour)
        for min_base in range(12):
            minute = min_base * 5
            if minute < 10:
                minute = "0"+str(minute)
            data[f"{hour}:{minute}:00"] = 0
    return data


def date_range(starting_day: date, num_days: int) -> List[date]:
    """
    Return a list of dates between a given date and a number of days previous.
    """
    date_list = []
    for i in reversed(range(num_days)):
        current_date = starting_day - timedelta(days=i)
        date_list.append(current_date.date())
    return date_list


def read_csv(dte: date, existing_data={}) -> Dict[str, int]:
    """
    Takes a date and returns data from that date. Data is appended to
    existing_data.
    """
    date_str = dte.strftime("%Y-%m-%d")
    full_path = os.path.join(DATA_DIR, date_str+".csv")

    if not os.path.isfile(full_path):
        return {}

    with open(full_path) as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for counter, row in enumerate(reader):
            if counter == 0:
                continue
            existing_data[row[0]] = int(row[1])
    return existing_data
