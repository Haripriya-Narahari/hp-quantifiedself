from celery import Celery
from flask import current_app as app
from flask_caching import *
from config import *
celery = Celery("Jobs")

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args,**kwargs)