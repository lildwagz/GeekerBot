import os
import time
import datetime
import schedule
from dhooks import Webhook, Embed

DB_HOST = 'localhost'
DB_USER = 'root'
DB_USER_PASSWORD = ''
DB_NAME = 'geekerbot'
BACKUP_PATH = 'dbbackup/'
DATETIME = time.strftime('%m%d%Y-%H%M%S')
TODAYBACKUPPATH = BACKUP_PATH + DATETIME
# hook = Webhook(
#     'https://discord.com/api/webhooks/791541534838620180/RS2RN_uQkRYvj73OkeX_9Ly19f4gkQBWDedkV0pWSJh6jwkMzlbR2FVbQYFCFpDOWQv_')
hook = Webhook(
    'https://discord.com/api/webhooks/803959715238510604/4ts6xrFVhGcNEUNjWuLvXF8tpcby07tyEefe6xfP2oxE7jASGaEeYv8582H5bGmqm4fU')


def job():
    start = time.monotonic()

    if not os.path.exists(TODAYBACKUPPATH):
        os.makedirs(TODAYBACKUPPATH)

    if os.path.exists(DB_NAME):
        file1 = open(DB_NAME)
        multi = 1
        # print("Starting backup of all dbs listed in file " + DB_NAME)
    else:
        # print("Databases file not found...")
        # print("Starting backup of database " + DB_NAME)
        multi = 0
    if multi:
        in_file = open(DB_NAME, "r")
        flength = len(in_file.readlines())
        in_file.close()
        p = 1
        dbfile = open(DB_NAME, "r")
        while p <= flength:
            db = dbfile.readline()
            db = db[:-1]
            dumpcmd = "mysqldump -u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + db + " > " + TODAYBACKUPPATH + "/" + db + ".sql"
            os.system(dumpcmd)
            p = p + 1
        dbfile.close()
        finish = (time.monotonic() - start) * 1000
        send_webhook_dbackup(finish)
        # print("mantap")
    else:
        db = DB_NAME
        dumpcmd = "mysqldump -u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + db + " > " + TODAYBACKUPPATH + "/" + db + ".sql"
        os.system(dumpcmd)
        finish = (time.monotonic() - start) * 1000
        send_webhook_dbackup(finish)
        # print("ok")


def send_webhook_dbackup(finish):
    embed = Embed(
        color=0x2fa737,
        timestamp='now'  # sets the timestamp to current time
    )

    imgdb = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQsCm6ydvCZQVXKhJQYWDugouy220jVK_eCrg&usqp=CAU'

    embed.set_author(name='Database Backup schedule', icon_url=imgdb)
    embed.add_field(name='Job :', value='`backing up all database` ', inline=True)
    embed.add_field(name='status :', value=f'`finished in {finish:.2f} ms`', inline=True)
    embed.set_footer(text='Powered By gabutcodex.tk')

    embed.set_thumbnail(imgdb)
    # embed.set_image(image2)

    hook.send(embed=embed)


schedule.every().day.at("20:28").do(job)

while True:
    # Checks whether a scheduled task
    # is pending to run or not
    schedule.run_pending()
    # time.sleep(1)
