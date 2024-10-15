from contextlib import closing

from celery import Celery
from celery.utils.log import get_task_logger

from celerys.dbmysql import dbmysql

apps2 = Celery('db-worker2',
              broker='redis:// lildwagz:lildwagz@redis-17460.c232.us-east-1-2.ec2.cloud.redislabs.com:17460',
              backend='redis:// lildwagz:lildwagz@redis-17460.c232.us-east-1-2.ec2.cloud.redislabs.com:17460',
              CELERY_ENABLE_UTC=True,
              timezone  = 'Etc/UTC')

logger = get_task_logger(__name__)


@apps2.task()
def get_guildtopgames(guildid):
    logger.info('Got Request - Starting work ')
    conn = dbmysql().DbConnect
    query = 'SELECT app_id, SUM(played) played_sum FROM tbl_gametime where guild_id=%s GROUP BY app_id ORDER BY ' \
            'played_sum DESC limit 10 ' % (str(guildid))
    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute(query)
            query_response = cursor.fetchall()
            logger.info('Success - fecthing the data gametime from database')
        cursor.close()
    except:
        logger.info('Failed - getting data gametime from database')
        cursor.close()
        return False
    logger.info('work finished')

    return query_response


@apps2.task()
def get_topgames(user_id, guildid):
    logger.info('Got Request - Starting work ')
    conn = dbmysql().DbConnect

    with closing(conn.cursor()) as cursor:
        cursor.execute('SELECT * FROM tbl_gametime WHERE user_id=%s and guild_id =%s ORDER BY played DESC LIMIT 5',
                       (str(user_id), guildid))
        logger.info('Success - fecthing the data from database')
        query_response = cursor.fetchall()

    cursor.close()

    logger.info('work finished')

    return query_response

@apps2.task()
def get_leaderboard(guildid):
    conn = dbmysql().DbConnect
    query = "SELECT * FROM tbl_users where guild_id = '%s' ORDER BY exp DESC" % (str(guildid))
    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute(query)
            query_response = cursor.fetchmany(10)
            logger.info('success - fetching leaderboard data from database')

    except:
        logger.info('failed - fetching leaderboard data from database')
        cursor.close()
        return False
    return query_response

@apps2.task()
def get_guild():
    conn = dbmysql().DbConnect
    try:
        with closing(conn.cursor()) as cursor:
            query = "SELECT guild_id FROM tbl_guilds"
            cursor.execute(query)
            response = cursor.fetchall()
            logger.info('Success - geting all guild id  from database')


    except:
        logger.info('Failed - gettinb data guild id from database')
        return False
    logger.info('work finished')
    return response


@apps2.task()
def get_users():
    conn = dbmysql().DbConnect
    try:
        with closing(conn.cursor()) as cursor:
            query = "SELECT * FROM `tbl_users` "
            cursor.execute(query)
            response = cursor.fetchall()
            logger.info('Success - geting all user id  from database')


    except:
        logger.info('Failed - gettinb data all user id from database')
        return False
    logger.info('work finished')
    return response


@apps2.task()
def get_all_user():
    conn = dbmysql().DbConnect
    query = 'SELECT * FROM tbl_users'
    # try:
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
        query_response = cursor.fetchall()
        logger.info('Success - fetching data user from database')
    cursor.close()
    return query_response


@apps2.task()
def get_minageaccount():
    conn = dbmysql().DbConnect
    query = "SELECT guild_id,minageaccount FROM tbl_settings"
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
        sq = cursor.fetchall()
        if not sq:
            return False
        conn.commit()
    cursor.close()
    return sq

@apps2.task()
def get_spamchannel():
    conn = dbmysql().DbConnect
    query = "SELECT guild_id,allowSpam FROM tbl_settings"
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
        sq = cursor.fetchall()
        if not sq:
            return False
        conn.commit()
    cursor.close()
    return sq

@apps2.task()
def get_infractionchannel():
    conn = dbmysql().DbConnect
    query = "SELECT guild_id,infractionchannel FROM tbl_settings"
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
        sq = cursor.fetchall()
        if not sq:
            return False
        conn.commit()
    cursor.close()
    return sq


@apps2.task()
def get_allguildtoogle():
    conn = dbmysql().DbConnect
    query = "SELECT guild_id,guildtopgames,imgwelcome_toggle,levelsystem_toggle,antiSpam,automod,captcha," \
            "antitoxic,antiLinks,ageaccount_toggle,triggerword_toogle,triggerrole_toogle FROM tbl_settings"
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
        sq = cursor.fetchall()
        if not sq:
            return False
        conn.commit()
    cursor.close()
    return sq

@apps2.task()
def get_autorole():
    conn = dbmysql().DbConnect
    query = "SELECT guild_id,role_id FROM tbl_autorole"
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
        sq = cursor.fetchall()
        if not sq:
            return False
        conn.commit()
    cursor.close()
    return sq

@apps2.task()
def get_all_warns():
    logger.info('Got Request - Starting work ')
    conn = dbmysql().DbConnect
    query = 'SELECT * FROM tbl_warns'
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
        query_response = cursor.fetchall()
    cursor.close()
    return query_response

@apps2.task()
def get_global_user_data(user_id, guildid):
    logger.info('Got Request - Starting work ')
    conn = dbmysql().DbConnect
    query = 'SELECT * FROM tbl_users WHERE user_id=%s and guild_id=%s' % (str(user_id), str(guildid))
    # try:
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
        query_response = cursor.fetchone()
        logger.info('Success - fetching data user from database')
        if not query_response:
            code = int(user_id) + int(guildid) - int(user_id * 2)
            query = "INSERT INTO tbl_users VALUES ('%s','%s','%s','%s','%s','%s')" % (
                f"USR{code}", str(user_id), guildid, 1, 0, 0)
            cursor.execute(query)
            conn.commit()
            logger.info('Success - inserting  data users into tbl_users')
            cursor.close()

    # except:
    #     logger.info('failed - getting  user data from database')
    #     cursor.close()
    #     return False
    return query_response



@apps2.task()
def get_prefix():
    conn = dbmysql().DbConnect
    query = f"SELECT guild_id,prefix FROM tbl_settings"
    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute(query)
            sq = cursor.fetchall()
            if not sq:
                return False
            conn.commit()
    except:
        return False
    cursor.close()
    return sq

@apps2.task()
def get_triggeredowrd():
    conn = dbmysql().DbConnect
    query = f"SELECT * FROM `tbl_triggerword`"
    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute(query)
            sq = cursor.fetchall()
            if not sq:
                return False
            conn.commit()
    except:
        return False
    cursor.close()
    return sq

@apps2.task()
def get_triggeredrole():
    conn = dbmysql().DbConnect
    query = f"SELECT * FROM `tbl_triggerrole`"
    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute(query)
            sq = cursor.fetchall()
            if not sq:
                return False
            conn.commit()
    except:
        return False
    cursor.close()
    return sq

@apps2.task()
def get_whitelistroles():
    conn = dbmysql().DbConnect
    query = f"SELECT * FROM `tbl_whitelistroles`"
    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute(query)
            sq = cursor.fetchall()
            if not sq:
                return False
            conn.commit()
    except:
        return False
    cursor.close()
    return sq
