from celery import Celery, Task

app = Celery('celery', include=['cogs.celery.db', ])


if __name__ == '__main__':
    app.start()
