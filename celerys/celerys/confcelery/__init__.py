import pymysql


broker_url = 'redis://127.0.0.1:6379/0'
result_backend = 'redis://127.0.0.1:6379/1'
broker_connection_max_retries = True
broker_connection_retry = 0
imports = ('celerys.db',)
include = ['celerys']
task_cls = 'celerys.db:DatabaseTask'
timezone = ''



# Sql config
MYSQL_HOST = "gabutcodex.tk"
MYSQL_USER = "mroosvelt"
MYSQL_PASS = "123lildwagz"
MYSQL_DB = "mroosvelt_geekerbot"


def mysqlcon(self):
    DbCon = pymysql.connect(
        host=MYSQL_HOST, user=MYSQL_USER,
        password=MYSQL_PASS,
        db=MYSQL_DB)

