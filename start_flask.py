#!/bin/bash

source venv/bin/activate
cd src/
FLASK_APP=start.py flask run --host=0.0.0.0 --debug
