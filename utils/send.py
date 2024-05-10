from bot import os
from bot import discord

async def send_message_long(send_func, message):
	with open("tmp", "w") as f:
		f.write(message)
	with open("tmp", "r") as f:
		retv = await send_func(
			f"Message too long. see attachment for more",
			file=discord.File(f, "message.txt")
		)
	if os.path.exists("tmp"):
		os.remove("tmp")

	return retv

async def send_message_short(send_func, message):
	return await send_func(message)

def get_send_func(context):
	send_func = None
	if isinstance(context, discord.Interaction):
		if context.response.is_done():
			send_func = context.followup.send
		else:
			send_func = context.response.send_message
	elif isinstance(context, discord.ext.commands.Context):
		send_func = context.send
	elif isinstance(context, discord.User):
		send_func = context.send
	elif isinstance(context, discord.TextChannel):
		send_func = context.send
	return send_func

async def send_message(context, message):
	send_func = get_send_func(context)
	if send_func == None:
		print("Error getting send_func from context")
		return

	if len(message) >= 2000:
		return await send_message_long(send_func, message)
	else:
		return await send_message_short(send_func, message)

async def send_embed(context, embed):
	send_func = get_send_func(context)
	if send_func == None:
		print("Error getting send_func from context")
		return
	await send_func(embed=embed)
