# from transformers import AutoModelForCausalLM, AutoTokenizer
# import torch
# tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
# model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
#
# def chatbot_response_b(step,user):
#     new_user_input_ids = tokenizer.encode(user + tokenizer.eos_token, return_tensors='pt')
#
#     bot_input_ids = torch.cat([step, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids
#     # print(bot_input_ids)
#     # generated a response while limiting the total chat history to 1000 tokens,
#     chat_history_ids_test = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)
#     x = tokenizer.decode(chat_history_ids_test[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
#     # pretty print last ouput tokens from bot
#     print("DialoGPT: {}".format(x))
#     return x
# from dhooks import Webhook, Embed
#
# hook = Webhook('https://discord.com/api/webhooks/791541534838620180/RS2RN_uQkRYvj73OkeX_9Ly19f4gkQBWDedkV0pWSJh6jwkMzlbR2FVbQYFCFpDOWQv_')
#
# embed = Embed(
#     description='I love you all :smiley:',
#     color=0x5CDBF0,
#     timestamp='now'  # sets the timestamp to current time
#     )
#
# image1 = 'https://images-ext-2.discordapp.net/external/c4tSz6HxEK9vmb4_88WpzSoWItK9W953jgIkx5iV4vE/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/791534486990356493/2270cbbbd5c496445bc6f4dfc938c50c.png'
# image2 = 'https://i.imgur.com/f1LOr4q.png'
#
# embed.set_author(name='geekerbot schedule', icon_url=image1)
# embed.add_field(name='shocking', value='its time to get your backpack :open_mouth:')
# embed.add_field(name='smiling', value='1234 :smile:')
# embed.set_footer(text='invite me to your discord server', icon_url=image1)
#
# embed.set_thumbnail(image1)
# embed.set_image(image2)
#
# hook.send(embed=embed)