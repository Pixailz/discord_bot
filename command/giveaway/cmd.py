from bot import time
from bot import discord
from discord.ext import commands

from bot import bot
from bot import print_user
from bot import get_embed
from bot import send_message
from bot import send_embed
from bot import is_allowed
from bot import get_random_bytes
from bot import GIVEAWAY

HDR_GIVEAWAY = "Giveaway:"

async def giveaway_check_name(ctx, name):
	if not name:
		await send_message(ctx, f"{HDR_GIVEAWAY} Need a giveaway name")
		return True
	if not name in GIVEAWAY:
		await send_message(ctx, f"{HDR_GIVEAWAY} No giveaway with name **{name}**")
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
		await send_message(ctx, f"{HDR_GIVEAWAY} No giveaway with name **{name}**")
		return

	with open("tmp", "w") as f:
		f.write(to_print)
	with open("tmp", "r") as f:
		await send_message(ctx, f"Giveaway details {name}\n{to_print}")

async def giveaway_create(ctx, name: str = None, arg_2: str = None):
	if name in GIVEAWAY:
		await send_message(ctx, f"{HDR_GIVEAWAY} already exist")
		return
	GIVEAWAY[name] = dict()
	await send_message(ctx, f"{HDR_GIVEAWAY} Created Giveaway `{name = }`")

async def giveaway_register(ctx, name):
	if not ctx.message.reference:
		await send_message(ctx, f"{HDR_GIVEAWAY} Reply to message for register a giveaway")
		return

	if await giveaway_check_name(ctx, name):
		return

	GIVEAWAY[name]["id_message"] = ctx.message.reference.message_id
	GIVEAWAY[name]["id_channel"] = ctx.message.channel.id
	GIVEAWAY[name]["id_guild"] = ctx.message.guild.id

	await send_message(f"{HDR_GIVEAWAY} Registred message, `{ctx.message.reference.message_id}`, for giveaway **{name}**")

async def giveaway_winner(ctx, name):
	if await giveaway_check_name(ctx, name):
		return

	if not GIVEAWAY[name].get("user_in"):
		await send_message(ctx, f"{HDR_GIVEAWAY} No user registred for giveaway **{name}**")
		return

	nb_user = len(GIVEAWAY[name]["user_in"])
	if nb_user == 0:
		await send_message(ctx, f"{HDR_GIVEAWAY} No user registred for giveaway **{name}** :'(")
		return

	id_winner = GIVEAWAY[name]["user_in"][get_random_bytes(4) % nb_user]

	message = await send_message(ctx, "And the Winner is")
	time.sleep(1)
	await message.edit(content="And the Winner is .")
	time.sleep(1)
	await message.edit(content="And the Winner is ..")
	time.sleep(1)
	await message.edit(content="And the Winner is ...")
	time.sleep(1)
	message = await send_message(ctx, f"And the Winner is **<@{id_winner}>** ({id_winner})")

async def	giveaway_get_message(channel, id):
	messages = [message async for message in channel.history(limit=500)]
	for m in messages:
		if m.id == id:
			return m

	return None

async def	giveaway_sync():
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
					await send_message(get_user(user), f"**Successfully** joined the giveaway id __{ga}__")

	print("Synchronised giveaways")

async def giveaway_embed(ctx, title, desc):
	title = title or "GIVEAWAY"
	desc = desc or "This is a giveaway"
	embed = get_embed(ctx, f"🎊 {title} 🎊", desc)
	embed.add_field(
		name="How to join",
		value="Just react with :white_check_mark: to this message and you "
		"will receive message once joined"
	)
	embed.set_footer(text="by Pixailz")
	await send_embed(ctx, embed)

@bot.command(
	name="px_giveaway",
	description="Manage giveaway",
	usage="create|register|winner|list|sync|embed [arg_1=None] [arg_2=None]",
)
@is_allowed()
async def giveaway_cmd(ctx, cmd: str = None, arg_1: str = None, arg_2: str = None):
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
		case "embed":
			await giveaway_embed(ctx, arg_1, arg_2)
		case _:
			await send_message(ctx, f"GIVEAWAY: cmd {cmd} not found")
