from bot import discord

from bot import get_user
from bot import r
from bot import bot
from bot import have_role
from bot import have_roles
from bot import send_message
from bot import MODERATED_GUILD
from bot import IDS
from bot import variate_word


WHITELIST_MODERATION = [
	# IDS["USER"]["pix"],
	IDS["USER"]["poney"],
	IDS["USER"]["kelly"],
	# IDS["USER"]["arty"],
	IDS["USER"]["bot_counting"],
	IDS["USER"]["bot_dyno"],
	IDS["USER"]["bot_mee6"],
]

async def moderate_message_url(msg):
	match = r.link.match(msg.content)
	if match:
		await msg.delete()
		await send_message(msg.channel, f"{msg.author.mention}, you can't send link")
		print(f"MODERATE_MESSAGE_URL: {msg.author} cannot send link in {msg.guild}")
		print(f"> '{msg.content}'")

async def moderate_message_words(msg):
	lowered = msg.content.lower()
	for word in MODERATED_GUILD[msg.guild.id]["words"]:
		for w in variate_word(word):
			if w in lowered:
				await msg.delete()
				await send_message(msg.channel, f"{msg.author.mention}, you can't say that word here!")
				print(f"MODERATE_MESSAGE_WORDS: {msg.author} send {word} in {msg.guild}")
				print(f"> '{msg.content}'")
				return True
	return False

def should_moderate_url(msg):
	roles = IDS["ROLE"].get(str(msg.guild.id), None)
	if roles == None:
		return False
	if have_roles(msg.author, roles["cannot_send_link"]):
		return True
	if have_roles(msg.author, roles["can_send_link"]):
		return False
	return True

def should_moderate_word(msg):
	return True

async def moderate_message(msg):
	for mode in MODERATED_GUILD[msg.guild.id].keys():
		match mode:
			case "url":
				if should_moderate_url(msg):
					await moderate_message_url(msg)
			case "words":
				if should_moderate_word(msg):
					await moderate_message_words(msg)

def should_moderate_message(msg):
	if msg.author.bot:
		return False
	if msg.author.id in WHITELIST_MODERATION:
		return False
	return True

LAST_RECEIVED = None

@bot.event
async def on_message(msg):
	if getattr(msg, "guild"):
		if msg.guild.id in MODERATED_GUILD.keys():
			if should_moderate_message(msg):
				await moderate_message(msg)
	else:
		if msg.author.id != IDS["USER"]["pix"] and msg.author.id != bot.user.id:
			await send_message(
				get_user(IDS["USER"]["pix"]),
				f"Message from {msg.author}:\n```\n{msg.content}\n```"
			)
	await bot.process_commands(msg)
