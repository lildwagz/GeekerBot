from contextlib import closing

from celery import Celery
from celery.utils.log import get_task_logger

# from celerys.dbmysql import dbmysql
from celerys.dbmysql import dbmysql

apps = Celery('db-worker',
              broker='redis:// lildwagz:lildwagz@redis-10450.c81.us-east-1-2.ec2.cloud.redislabs.com:10450',
              backend='redis:// lildwagz:lildwagz@redis-10450.c81.us-east-1-2.ec2.cloud.redislabs.com:10450',
              CELERY_ENABLE_UTC=True,
              timezone  = 'Etc/UTC')
# apps = Celery('db-worker', broker='redis://127.0.0.1:6379/0', backend='redis://127.0.0.1:6379/0')

task_acks_late = True
worker_prefetch_multiplier = 1
logger = get_task_logger(__name__)



@apps.task()
def initialize_guild(guild_id):
    logger.info('Got Request - Starting work ')
    conn = dbmysql().DbConnect

    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute(f"SELECT * FROM tbl_guilds WHERE guild_id= {guild_id};")
            sql = cursor.fetchone()
            if sql:
                pass
            else:
                cursor.execute(f"INSERT INTO tbl_guilds (`guild_id`) VALUES ({guild_id});")
                conn.commit()
            cursor.execute(f"SELECT * FROM tbl_settings WHERE guild_id= {guild_id};")
            sql = cursor.fetchone()
            if sql:
                pass
            else:
                cursor.execute(f"INSERT INTO tbl_settings (guild_id) VALUES ({guild_id});")
                cursor.execute(f"INSERT INTO tbl_autorole (guild_id) VALUES ({guild_id});")
                conn.commit()
                logger.info('Success - inserting the data guild in to database')
            cursor.close()
    except:
        logger.info('failed - inserting data guild')
        cursor.close()
        return False
    logger.info('work finished')

    return True




@apps.task()
def insert_new_member(guildidid, member, code):
    # logger.info('Got Request - Starting work ')
    conn = dbmysql().DbConnect
    query = 'select * from tbl_users where user_id =%s and guild_id=%s' % (str(member), str(guildidid))
    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute(query)
            sql = cursor.fetchone()
            if sql:
                # logger.info('Success - user already exists in database')
                pass
            else:
                query = "INSERT INTO tbl_users VALUES ('%s','%s','%s','%s','%s','%s')" % (
                    str("USR" + code), str(member), guildidid, 1, 0, 0)
                cursor.execute(query)
                conn.commit()
                # logger.info('Success - inserting the data in to database')
            cursor.close()
    except:
        cursor.close()
        # logger.info('Failed - quering data user from database')
        return False
    # logger.info('work finished')
    return


@apps.task()
def remove_guild_id(guildid):
    logger.info('Got Request - Starting work ')
    conn = dbmysql().DbConnect
    query = "DELETE FROM tbl_guilds WHERE guild_id = %s" % (str(guildid))

    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute(query)
            conn.commit()
            cursor.close()
            logger.info('Success - deleting data guild from database')
    except:
        cursor.close()
        logger.info('Failed - quering data guild_id from database')
        return False
    logger.info('work finished')
    return


@apps.task()
def remove_member(usedid, guildid):
    logger.info('Got Request - Starting work ')
    conn = dbmysql().DbConnect

    try:
        query = "DELETE FROM tbl_users WHERE user_id =%s and guild_id=%s" % (str(usedid), str(guildid))
        with closing(conn.cursor()) as cursor:
            cursor.execute(query)
            conn.commit()
            cursor.close()
            logger.info('Success - deleting data user from database')

    except:
        cursor.close()
        logger.info('Failed - quering data user from database')
        return

    logger.info('work finished')

    return




@apps.task()
def roles_to_db(guild_id, role_name, role_id):
    logger.info('Got Request - Starting work ')
    conn = dbmysql().DbConnect
    try:
        with closing(conn.cursor()) as cursor:

            cursor.execute(f"SELECT role_id FROM tbl_roles WHERE role_id={str(role_id)} and guild_id={str(guild_id)}")
            sq = cursor.fetchone()
            logger.info('Success - searching role  from database')
            if sq:
                conn.commit()
                cursor.close()
                return True
            else:
                cursor.execute(f"INSERT INTO tbl_roles (guild_id, role_name, role_id) "
                               f"VALUES ('{guild_id}', '{str(role_name)}', '{str(role_id)}')")
                conn.commit()
                logger.info('Success - inserting  guild roles into database')
                cursor.close()
    except:
        logger.info('failed - quering  guild roles from database')
        cursor.close()
        return
    logger.info('work finished')
    return




@apps.task()
def set_user_data(user_id, user_level, user_exp, user_points, guildidid):
    logger.info('Got Request - Starting work ')
    conn = dbmysql().DbConnect
    query = "UPDATE tbl_users SET level='%s', exp='%s', points='%s' WHERE user_id='%s' and guild_id='%s'" % (
        user_level, user_exp, user_points, user_id, guildidid)
    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute(query)
            logger.info('Success - updating data user in to tbl_users')
            conn.commit()
            cursor.close()
    except:
        logger.info('failed - updating user data into tbl_users')
        cursor.close()
        return False
    return





@apps.task()
def insert_warn(kode_user: str, code: int, offender_name: str, position: int, user_id: int, warner: int,
                warner_name: str, reason: str, channel: int, datetime: int):
    logger.info('Got Request - Starting work ')
    conn = dbmysql().DbConnect
    query = f"SELECT * FROM tbl_warns WHERE kode_user='{str(kode_user)}' and code={code}"
    # try:
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
        sq = cursor.fetchone()
        logger.info('Success - searching user warns  from database')
        if sq:
            conn.commit()
            cursor.close()
            return True
        else:
            query = f"INSERT INTO tbl_warns (kode_user, code,offender_name,position,user_id,warner,warner_name," \
                    f"reason,channel,datetime) VALUES ('{kode_user}', {code}, '{offender_name}',{position},{user_id}," \
                    f"{warner},'{warner_name}','%s',{channel},'{datetime}') " % (str(reason))
            cursor.execute(query)
            conn.commit()
            logger.info(f'Success - inserting  {offender_name}  warn into tbl_warns')
            cursor.close()

    # except:
    #     logger.info('failed - quering  tbl_warns  from database')
    #     cursor.close()
    #     return
    logger.info('work finished')
    return


@apps.task()
def delete_warn(kode_user: str, code: int):
    logger.info('Got Request - Starting work ')
    conn = dbmysql().DbConnect
    query = f"DELETE FROM tbl_warns WHERE kode_user='{kode_user}' AND code={code}"
    # try:
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
        conn.commit()
        logger.info(f'Success - deleting  {kode_user}  warn from tbl_warns')
        cursor.close()

    # except:
    #     logger.info('failed - quering  tbl_warns  from database')
    #     cursor.close()
    #     return
    logger.info('work finished')
    return




@apps.task()
def change_prefix(guildid, prefix):
    conn = dbmysql().DbConnect
    query = f"UPDATE tbl_settings SET prefix='{prefix}' WHERE guild_id={guildid}"
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
        conn.commit()
    cursor.close()
    return



@apps.task()
def set_housminage(guildid, hours):
    conn = dbmysql().DbConnect
    query = f"UPDATE tbl_settings SET minageaccount={hours} WHERE guild_id={guildid}"
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
        conn.commit()
    cursor.close()
    return





@apps.task()
def set_spamchannel(guildid, channel):
    conn = dbmysql().DbConnect
    query = f"UPDATE tbl_settings SET allowSpam={channel} WHERE guild_id={guildid}"
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
        conn.commit()
    cursor.close()
    return




@apps.task()
def set_guildtoogle(guildid, toogle):
    conn = dbmysql().DbConnect
    query = f"UPDATE tbl_settings SET guildtopgames={toogle} WHERE guild_id={guildid}"
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
        conn.commit()
    cursor.close()
    return


@apps.task()
def set_leveltoogle(guildid, toogle):
    conn = dbmysql().DbConnect
    query = f"UPDATE tbl_settings SET levelsystem_toggle={toogle} WHERE guild_id={guildid}"
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
        conn.commit()
    cursor.close()
    return


@apps.task()
def set_antispamtoogle(guildid, toogle):
    conn = dbmysql().DbConnect
    query = f"UPDATE tbl_settings SET antiSpam={toogle} WHERE guild_id={guildid}"
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
        conn.commit()
    cursor.close()
    return


@apps.task()
def set_antitoxictoogle(guildid, toogle):
    conn = dbmysql().DbConnect
    query = f"UPDATE tbl_settings SET antitoxic={toogle} WHERE guild_id={guildid}"
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
        conn.commit()
    cursor.close()
    return


@apps.task()
def set_antilinkstoogle(guildid, toogle):
    conn = dbmysql().DbConnect
    query = f"UPDATE tbl_settings SET antiLinks={toogle} WHERE guild_id={guildid}"
    with closing(conn.cursor()) as cursor:
        cursor.execute(query)
        conn.commit()
    cursor.close()
    return


@apps.task()
def update_guildgames(userid, app_id, guildidid):
    conn = dbmysql().DbConnect
    with closing(conn.cursor()) as cursor:
        cursor.execute('SELECT * FROM tbl_gametime WHERE user_id=%s AND app_id=%s and guild_id=%s',
                       (userid, app_id, guildidid))
        query_response = cursor.fetchone()
        if not query_response:
            with closing(conn.cursor()) as cursor:
                cursor.execute('INSERT INTO tbl_gametime (user_id,guild_id,app_id,played) VALUES (%s,%s,%s,%s)',
                               (userid, guildidid, app_id, 1))
                conn.commit()
                cursor.close()
                return

        id, user_id, guild_id, app_id, gametime = query_response
        cursor.execute('UPDATE tbl_gametime SET played=%s WHERE user_id=%s AND app_id=%s and guild_id=%s ',
                       (str(gametime + 1), user_id, app_id, guildidid))
        conn.commit()
    cursor.close()
    return query_response

@apps.task()
def set_autorole(guildid,roleid):
    logger.info('Got Request - Starting work ')
    conn = dbmysql().DbConnect

    with closing(conn.cursor()) as cursor:
        query = f"UPDATE tbl_autorole SET role_id={roleid} where guild_id={guildid}"
        cursor.execute(query)
        conn.commit()
        logger.info(f'Success - updating  {roleid}  into tbl_autorole')
        cursor.close()

    # except:
    #     logger.info('failed - quering  tbl_warns  from database')
    #     cursor.close()
    #     return
    logger.info('work finished')
    return

@apps.task()
def set_triggerword(guildid,roleid,channel,word):
    conn = dbmysql().DbConnect

    conn = dbmysql().DbConnect
    query = 'select * from tbl_triggerword where  guild_id=%s' % (str(guildid))
    try:
        with closing(conn.cursor()) as cursor:
            cursor.execute(query)
            sql = cursor.fetchone()
            if sql:
                pass
            else:
                query = f"INSERT INTO tbl_triggerword  (`guild_id`,`word`,`	role`,`channel`) VALUES  ({guildid},{word},{roleid},{channel})"
                cursor.execute(query)
                conn.commit()
            cursor.close()
    except:
        cursor.close()
        # logger.info('Failed - quering data user from database')
        return False
    # logger.info('work finished')
    return



if __name__ == '__main__':
    apps.start()
