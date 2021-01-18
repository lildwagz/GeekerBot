import pymysql


class dbmysql():
    def __init__(self):
        # self.DbConnect = pymysql.connect(host="localhost", user="lildwagz",
        #                             password="lildwagz",
        #                             db="geekerbot")
        self.DbConnect = pymysql.connect(host="13.212.6.176", user="lildwagz",
                                         password="lildwagz",
                                         db="geekerbot")


