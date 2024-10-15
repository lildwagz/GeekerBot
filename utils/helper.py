"""
This helper script is helpful in some situations  like creating the ctx object out of the member object etc
"""
from asyncio import run_coroutine_threadsafe

from celery import Celery

from utils import default

'''
This class is designed to hold all data that the bot uses extensively and the class is designed in a way that it can
reload the data on change.
'''


class Cache:
    def __init__(self, bot):
        self.bot = bot
        self.prefixes = {}
        self.guildgame_toogle = {}
        self.levelsystem_toogle = {}
        self.imgwelcome_toggle = {}
        self.antiSpam_toogle = {}
        self.automod_toogle = {}
        self.captcha_toogle = {}
        self.antitoxic_toogle = {}
        self.antiLinks_toogle = {}
        self.ageaccount_toggle = {}
        self.warns=[]
        self.allowspam ={}
        self.captcha_channel = {}
        self.ageaccount = {}
        self.autorole = {}

        self.users = {}

        self.triger_word = {}
        self.trigerword_toogle = {}
        self.trigerrole_toogle = {}
        self.triger_role = {}

        self.whitelist = {}
        self.infractionchannel = {}

        bot.loop.create_task(self.initialize_settings_cache())

    async def initialize_settings_cache(self):
        result = self.bot.app2.send_task('celerys.worker2.get_prefix')
        if result.get():
            row = result.get()
            for guild_id, prefix in row:
                self.prefixes[str(guild_id)] = prefix
        else:
            print("kontol")

        # print(self.prefixes)

        result = self.bot.app2.send_task('celerys.worker2.get_allguildtoogle')

        if result.get():
            row = result.get()
            for guildid, games, imgwelcome, lvl, antispam, automod, captcha, antitoxic, antilink,ageaccount_toggle,trigerword_toogle,triggerrole_toogle in row:
                self.guildgame_toogle[str(guildid)] = bool(games)
                self.levelsystem_toogle[str(guildid)] = bool(lvl)
                self.imgwelcome_toggle[str(guildid)] = bool(imgwelcome)
                self.antiSpam_toogle[str(guildid)] = bool(antispam)
                self.automod_toogle[str(guildid)] = bool(automod)
                self.captcha_toogle[str(guildid)] = bool(captcha)
                self.antitoxic_toogle[str(guildid)] = bool(antitoxic)
                self.antiLinks_toogle[str(guildid)] = bool(antilink)
                self.ageaccount_toggle[str(guildid)] = bool(ageaccount_toggle)
                self.trigerword_toogle[str(guildid)] = bool(trigerword_toogle)
                self.trigerrole_toogle[str(guildid)] = bool(triggerrole_toogle)

        # print(self.guildgame_toogle)
        # print(self.levelsystem_toogle)
        # print(self.imgwelcome_toggle)
        # print(self.antiSpam_toogle)
        # print(self.automod_toogle)
        # print(self.captcha_toogle)
        # print(self.antitoxic_toogle)
        # print(self.antiLinks_toogle)

        resultq = self.bot.app2.send_task('celerys.worker2.get_all_user')
        if resultq.get():
            row = resultq.get()
            for kode_user, user_id, guild_id, user_level, user_exp, user_points in row:
                self.users[str(kode_user)] = user_id, guild_id, user_level, user_exp, user_points

        resultwarn = self.bot.app2.send_task('celerys.worker2.get_all_warns')
        if resultwarn.get():
            for id,i, code ,offender_n,position, user_id,warner_id, warner_name , reasons, channel, datetimes in resultwarn.get():
                # print(i)
                if self.bot.cache.warns:
                    for index, val in enumerate(self.bot.cache.warns):
                        if i in val.keys():
                            amount = len(self.bot.cache.warns[index][i])
                            new_amount = amount + 1
                            data = {
                                new_amount: [offender_n, position, user_id, warner_id, warner_name, reasons, channel,
                                             datetimes]
                            }
                            self.bot.cache.warns[index][i].append(data)
                            pass
                    new_amount = code
                    data = {
                        i: [{new_amount: [offender_n, position, user_id, warner_id, warner_name, reasons,
                                          channel, datetimes]}]
                    }
                    self.bot.cache.warns.append(data)

                else:
                    new_amount = code
                    data = {
                        i: [{new_amount: [offender_n, position, user_id, warner_id, warner_name, reasons, channel,
                                          datetimes]}]
                    }
                    self.bot.cache.warns.append(data)

        # print(self.warns)
        resultallowspam = self.bot.app2.send_task('celerys.worker2.get_spamchannel')

        if resultallowspam.get():
            row = resultallowspam.get()
            for guildid, allowspam in row:
                self.allowspam[str(guildid)] = allowspam

        resultallminage = self.bot.app2.send_task('celerys.worker2.get_minageaccount')
        if resultallminage.get():
            row = resultallminage.get()
            for guildid, minage in row:
                self.ageaccount[str(guildid)] = minage

        resultautorole = self.bot.app2.send_task('celerys.worker2.get_autorole')
        if resultautorole.get():
            row = resultautorole.get()
            for guildid, roleid in row:
                self.autorole[str(guildid)] = roleid

        resulttriggeredword = self.bot.app2.send_task('celerys.worker2.get_triggeredowrd')
        if resulttriggeredword.get():
            row = resulttriggeredword.get()
            for guildid, word ,role , channel in row:
                self.triger_word[str(guildid)] = [word, role, channel]

        resulttriggeredrole = self.bot.app2.send_task('celerys.worker2.get_triggeredrole')
        if resulttriggeredrole.get():
            row = resulttriggeredrole.get()
            for guildid, newrole, oldrole in row:
                self.triger_role[str(guildid)] = [newrole, oldrole]

        resulwhitelistroles = self.bot.app2.send_task('celerys.worker2.get_whitelistroles')
        if resulwhitelistroles.get():
            row = resulwhitelistroles.get()
            for id, guildid, roles in row:
                try:
                    if self.bot.cache.whitelist[str(guildid)] is None:
                        self.bot.cache.whitelist[str(guildid)] = roles

                    else:
                        self.bot.cache.whitelist[str(guildid)].append(roles)

                        if not len(self.bot.cache.whitelist[str(guildid)]) != len(
                                set(self.bot.cache.whitelist[str(guildid)])):
                            pass
                        else:
                            self.bot.cache.whitelist[str(guildid)] = list(
                                dict.fromkeys(self.bot.cache.whitelist[str(guildid)]))

                except KeyError:
                    self.bot.cache.whitelist[str(guildid)] = [roles]

        resultinfraction = self.bot.app2.send_task('celerys.worker2.get_infractionchannel')

        if resultinfraction.get():
            row = resultinfraction.get()
            for guildid, channel in row:
                self.infractionchannel[str(guildid)] = channel