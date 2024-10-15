import os

import discord
from better_profanity import profanity


from utils import default, permissions
from utils.bot import Bot
from utils.utilss import determine_prefix

config = default.get("config.json")
print("Logging in...")
intents = discord.Intents().all()



bot = Bot(
    command_prefix=determine_prefix,
    prefix=determine_prefix,
    owner_ids=config.owners,
    command_attrs=dict(hidden=True),
    intents=intents

)
bot.remove_command("help")  # To create a personal help command

if os.path.exists('assets/blacklistedword.txt'):
    profanity.load_censor_words_from_file('assets/blacklistedword.txt')
else:
    print('The custom profanity file is not satisfied, the default profanity file will be used.')
    profanity.load_censor_words()

for file in os.listdir("cogs/"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

for file in os.listdir("cogs/listener"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.listener.{name}")


try:
    bot.run(config.token)
except Exception as e:
    print(f'Error when logging in: {e}')
