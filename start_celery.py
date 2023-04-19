#!/bin/sh

cd src
celery -A start.celery beat
