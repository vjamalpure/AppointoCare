from celery import Celery


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config.get("broker_url"),
        backend=app.config.get("result_backend")
    )
    celery.conf.update(app.config)
    celery.conf.enable_utc = True
    celery.conf.timezone = "UTC"

    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery
