#!/bin/bash

source venv/bin/activate
cd src
celery -A start.celery beat -s /tmp/co2-celerybeat-schedule
