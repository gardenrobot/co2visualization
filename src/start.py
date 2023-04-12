from flaskapp import app, celery
from tasks import sensorread


# TODO change the read interval into a cron
READ_INTERVAL = 300.0 # 5 minutes


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(READ_INTERVAL, sensorread)
