from bot import time
from bot import discord
from discord.ext import commands

from bot import bot
from bot import print_user
from bot import extended_check
from bot import get_random_bytes
from bot import GIVEAWAY

HDR_GIVEAWAY = "Giveaway:"

async def giveaway_check_name(ctx, name):
	if not name:
		await ctx.send(f"{HDR_GIVEAWAY} Need a giveaway name")
		return True
	if not name in GIVEAWAY:
		await ctx.send(f"{HDR_GIVEAWAY} No giveaway with name **{name}**")
		return True
	return False

def giveaway_list_one(name):
	to_print = str()
	if "id_message" in GIVEAWAY[name]:
		to_print += f"    - id_message: {GIVEAWAY[name]['id_message']}\n"
	if "user_in" in GIVEAWAY[name] and len(GIVEAWAY[name]['user_in']):
		to_print += f"    - user_in ({len(GIVEAWAY[name]['user_in'])}):\n"
		for i in GIVEAWAY[name]["user_in"]:
			to_print += f"      - {print_user(i)}\n"
	if "user_out" in GIVEAWAY[name] and len(GIVEAWAY[name]['user_out']):
		to_print += f"    - user_out ({len(GIVEAWAY[name]['user_out'])}):\n"
		for i in GIVEAWAY[name]["user_out"]:
			to_print += f"      - {print_user(i)}\n"
	return to_print

def giveaway_list_all():
	to_print = "Giveaways:\n"
	for k in GIVEAWAY.keys():
		to_print += "  - " + k + "\n"
		to_print += giveaway_list_one(k)
	return to_print

def giveaway_list_specific(name):
	to_print = f"Giveaway \"{name}\":\n"
	return to_print + giveaway_list_one(name)

async def giveaway_list(ctx, name):
	if not name:
		to_print = giveaway_list_all()
	elif name in GIVEAWAY:
		to_print = giveaway_list_specific(name)
	else:
		await ctx.send(f"{HDR_GIVEAWAY} No giveaway with name **{name}**")
		return

	with open("tmp", "w") as f:
		f.write(to_print)
	with open("tmp", "r") as f:
		await ctx.send(f"Giveaway details {name}", file=discord.File(f, "list_giveaway.txt"))

async def giveaway_create(ctx, name: str = None, arg_2: str = None):
	if name in GIVEAWAY:
		await ctx.send(f"{HDR_GIVEAWAY} already exist")
		return
	GIVEAWAY[name] = dict()
	await ctx.send(f"{HDR_GIVEAWAY} Created Giveaway `{name = }`")

async def giveaway_register(ctx, name):
	if not ctx.message.reference:
		await ctx.send(f"{HDR_GIVEAWAY} Reply to message for register a giveaway")
		return

	if await giveaway_check_name(ctx, name):
		return

	GIVEAWAY[name]["id_message"] = ctx.message.reference.message_id
	GIVEAWAY[name]["id_channel"] = ctx.message.channel.id
	GIVEAWAY[name]["id_guild"] = ctx.message.guild.id

	await ctx.send(f"{HDR_GIVEAWAY} Registred message, `{ctx.message.reference.message_id}`, for giveaway **{name}**")

async def giveaway_winner(ctx, name):
	if await giveaway_check_name(ctx, name):
		return

	if not GIVEAWAY[name].get("user_in"):
		await ctx.send(f"{HDR_GIVEAWAY} No user registred for giveaway **{name}**")
		return

	nb_user = len(GIVEAWAY[name]["user_in"])
	if nb_user == 0:
		await ctx.send(f"{HDR_GIVEAWAY} No user registred for giveaway **{name}** :'(")
		return

	id_winner = GIVEAWAY[name]["user_in"][get_random_bytes(4) % nb_user]

	message = await ctx.send(f"And the Winner is **<@{id_winner}>** ({id_winner})")
	# time.sleep(1)
	# await message.edit(content="And the Winner is .")
	# time.sleep(1)
	# await message.edit(content="And the Winner is ..")
	# time.sleep(1)
	# await message.edit(content="And the Winner is ...")
	# time.sleep(1)
	# await message.edit(content=f"And the Winner is ")

async def	giveaway_get_message(channel, id):
	messages = [message async for message in channel.history(limit=500)]
	for m in messages:
		if m.id == id:
			return m

	return None

async def	giveaway_sync():
	from pprint import pprint
	for ga in GIVEAWAY:
		if "id_message" in GIVEAWAY[ga]:
			id_guild = GIVEAWAY[ga].get(str("id_guild"), None)
			if not id_guild:
				print(f"guild id not found ({ga})")
				continue
			guild = bot.get_guild(id_guild)
			if not guild:
				print(f"guild not found ({ga})")
				continue
			id_channel = GIVEAWAY[ga].get(str("id_channel"), None)
			if not id_channel:
				print(f"channel id not found ({ga})")
				continue
			channel = guild.get_channel(id_channel)
			if not channel:
				print(f"channel not found ({ga})")
				continue

			message = await giveaway_get_message(channel, GIVEAWAY[ga]["id_message"])
			if not message:
				print(f"message not found ({ga})")
				continue

			to_add = list()
			for reaction in message.reactions:
				async for user in reaction.users():
					if not user.id in to_add:
						to_add.append(user.id)

			for user in to_add:
				if not user in GIVEAWAY[ga]["user_in"]:
					GIVEAWAY[ga]["user_in"].append(user)
					print(f"added {user} to {ga}")
					user = bot.get_user(user)
					await user.send(f"**Successfully** joined the giveaway id __{ga}__")

	print("Synchronised giveaways")

@commands.command(
	description="Manage giveaway",
	usage="create|register|winner|list [arg_1=None] [arg_2=None]",
	checks=[extended_check],
)
async def giveaway(ctx, cmd: str, arg_1: str = None, arg_2: str = None):
	match cmd:
		case "create":
			await giveaway_create(ctx, arg_1, arg_2)
		case "register":
			await giveaway_register(ctx, arg_1)
		case "winner":
			await giveaway_winner(ctx, arg_1)
		case "list":
			await giveaway_list(ctx, arg_1)
		case "sync":
			await giveaway_sync()
		case _:
			await ctx.send(f"GIVEAWAY: cmd {cmd} not found")
