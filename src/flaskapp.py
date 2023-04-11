from flask import Flask
from chartkick.flask import chartkick_blueprint
from flask_celeryext import FlaskCeleryExt


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
