import os
import csv

from chartkick.flask import chartkick_blueprint, PieChart, LineChart
from datetime import datetime, date, timedelta
from flask import Flask, render_template
from flask_celeryext import FlaskCeleryExt
from typing import Dict, List

from common import date_to_str, DATA_DIR

from celery.schedules import crontab


CHART_TEMPLATE = "chart.template"

app = Flask("testapp")
app.config.update(dict(
    CELERY_ALWAYS_EAGER=True,
    CELERY_RESULT_BACKEND="cache",
    CELERY_CACHE_BACKEND="memory",
    CELERY_EAGER_PROPAGATES=True),
    CELERY_BROKER_URL="redis://redis:6379", # TODO read these from config file / docker-compose
)
app.register_blueprint(chartkick_blueprint, template_folder='templates/')
ext = FlaskCeleryExt()
ext.init_app(app)
celery = ext.celery


celery.conf.beat_schedule = {
        'sensorread': {
            'task': 'tasks.sensorread',
            'schedule': crontab(minute="*/5"),
        },
    }


@app.route("/test")
def test():
    chart = PieChart({"Blueberry": 44, "Strawberry": 23})
    return render_template(CHART_TEMPLATE, chart=chart)


@app.route("/")
def linechart():
    data = read_csv(datetime.now())
    chart = LineChart(data, xtitle="Time", ytitle="CO2 in ppm")
    return render_template(
        CHART_TEMPLATE,
        chart=chart,
        current_co2=get_current_co2(),
    )


@app.route("/7dayoverlap")
def overlap():

    data = [{
        "name": "baseline",
        "data": create_baseline(),
        "color": "#ffffff00",
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
            "color": "#00000040",
        })

    chart = LineChart(data, xtitle="Time", ytitle="CO2 in ppm")
    return render_template(
        CHART_TEMPLATE,
        chart=chart,
        current_co2=get_current_co2(),
    )


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


def read_csv(dte: date, existing_data: Dict = None) -> Dict[str, int]:
    """
    Takes a date and returns data from that date. Data is appended to
    existing_data.
    """
    existing_data = existing_data or {}
    date_str = dte.strftime("%Y-%m-%d")
    full_path = os.path.join(DATA_DIR, date_str+".csv")

    if not os.path.isfile(full_path):
        return {}

    with open(full_path) as csvfile:
        reader = csv.reader(csvfile, delimiter=",") #TODO remove this delimiter everywhere
        for counter, row in enumerate(reader):
            if counter == 0:
                continue
            existing_data[row[0]] = int(row[1])
    return existing_data


def get_current_co2() -> int: # TODO make this return None when value is over 20minutes old
    today = date_to_str(date.today())
    today_path = os.path.join(DATA_DIR, today+".csv")
    with open(today_path) as csvfile:
        lastline = csvfile.readlines()[-1]
        current_co2 = lastline.split(",")[1]
    return current_co2
