from abc import ABC

from celery import Task

from cogs.func.dbmysql import dbmysql


class DatabaseTask(Task, ABC):
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = dbmysql().DbConnect
        if self._db.is_connected():
            return self._db
        else:
            self._db = dbmysql().DbConnect
            return self._db
