# CO2 Visualization

A tool for logging data from a co2meter.com sensor and visualizing it.

Built with [co2meter](https://github.com/vfilimonov/co2meter), Flask, and Celery. Can be optionally deployed with docker compose.

TODO put pics of graphs and hardware here

## Setup

1. Set up a Redis server.
1. `mkdir data`
1. Copy `config.toml.template` to `config.toml` and set options.
1. `virtualenv venv && source venv/bin/activate && pip install -r requirements.txt`
1. `./start_celery.py`
1. `./start_flask.py`

## Setup (Docker Compose)

1. `mkdir data`
1. Copy `config.toml.template` to `config.toml` and set options.
1. Run `update_device.sh` to find the USB device and update the docker compose config.
   - This will need to be updated every time the machine is rebooted or the device is unplugged.
1. `docker-compose up -d`
