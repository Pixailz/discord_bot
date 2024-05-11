from bot import Union
from bot import time
from bot import discord
from discord.ext import commands
from bot import Literal

from bot import get_embed
from bot import print_user
from bot import is_allowed
from bot import send_message
from bot import send_embed
from bot import get_mee6_leaderboard
from bot import get_random_bytes
from bot import get_user
from bot import GIVEAWAY

async def px_autocomplete_giveaway_name(ctx, current: str):
	if len(current) == 0:
		return [ discord.app_commands.Choice(name=ga_id, value=ga_id)
			for ga_id in GIVEAWAY.keys()
		]

class GiveawayCOG(
		commands.Cog,
		name="Giveaway",
	):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	# EVENT
	@commands.Cog.listener()
	async def on_ready(self):
		print("Giveaway cog loading")
		print("------")
		await giveaway_sync(self.bot)
		print("------")
		print("Giveaway cog loaded")

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		giveaway_id = message_to_giveaway(payload.message_id)
		if giveaway_id and await giveaway_can_join(payload, giveaway_id):
			if not "user_in" in GIVEAWAY[giveaway_id]:
				GIVEAWAY[giveaway_id]["user_in"] = list()
			if not "user_out" in GIVEAWAY[giveaway_id]:
				GIVEAWAY[giveaway_id]["user_out"] = list()

			if not payload.user_id in GIVEAWAY[giveaway_id]["user_in"]:
				GIVEAWAY[giveaway_id]["user_in"].append(payload.user_id)
			if payload.user_id in GIVEAWAY[giveaway_id]["user_out"]:
				GIVEAWAY[giveaway_id]["user_out"].remove(payload.user_id)

			print(f"GIVEAWAY: added {payload.user_id} to {giveaway_id}")
			await send_message(
				get_user(payload.user_id),
				f"**Successfully** joined the giveaway id __{giveaway_id}__"
			)

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		giveaway_id = message_to_giveaway(payload.message_id)
		if giveaway_id:
			if not "user_out" in GIVEAWAY[giveaway_id]:
				GIVEAWAY[giveaway_id]["user_out"] = list()
			if not "user_in" in GIVEAWAY[giveaway_id]:
				GIVEAWAY[giveaway_id]["user_in"] = list()

			if not payload.user_id in GIVEAWAY[giveaway_id]["user_out"]:
				GIVEAWAY[giveaway_id]["user_out"].append(payload.user_id)
			if payload.user_id in GIVEAWAY[giveaway_id]["user_in"]:
				GIVEAWAY[giveaway_id]["user_in"].remove(payload.user_id)

			print(f"GIVEAWAY: removed {payload.user_id} to {giveaway_id}")
			await send_message(
				get_user(payload.user_id),
				f"**Successfully** leaved the giveaway id __{giveaway_id}__",
			)

	@commands.hybrid_group(name="px_giveaway", description="Manage giveaway")
	async def px_giveaway(self, ctx):
		pass

	@px_giveaway.command(
		name="create",
		description="Create a giveaway, given a giveaway name"
	)
	@discord.app_commands.describe(
		name = "The name of the giveaway, should not be already created",
	)
	@is_allowed()
	async def giveaway_create(self, ctx, name: str):
		if name in GIVEAWAY:
			await send_message(ctx, f"GIVEAWAY: already exist")
			return
		GIVEAWAY[name] = dict()
		await send_message(ctx, f"GIVEAWAY: Created Giveaway `{name = }`")

	@px_giveaway.command(
		name="register",
		description="Register a giveaway, given a giveaway name and a replied message"
	)
	@discord.app_commands.describe(
		name = "The name of the giveaway, should be already created",
	)
	@discord.app_commands.autocomplete(
		name = px_autocomplete_giveaway_name
	)
	@is_allowed()
	async def giveaway_register(self, ctx,
		name: str,
		message: discord.Message,
	):
		# if not ctx.message.reference:
		# 	await send_message(ctx, f"GIVEAWAY: Reply to message for register a giveaway")
		# 	return

		if await giveaway_check_name(ctx, name):
			return

		GIVEAWAY[name]["id_message"] = message.id
		GIVEAWAY[name]["id_channel"] = message.channel.id
		GIVEAWAY[name]["id_guild"] = message.guild.id

		await send_message(ctx,
			f"GIVEAWAY: Registred message, `{message.id}`"
			f" for giveaway **{name}**"
		)

	@px_giveaway.command(
		name="winner",
		description="Get a winner, given a giveaway name"
	)
	@discord.app_commands.describe(
		name = "The name of the giveaway, should be already created",
	)
	@discord.app_commands.autocomplete(
		name = px_autocomplete_giveaway_name
	)
	@is_allowed()
	async def giveaway_winner(self, ctx, name):
		if await giveaway_check_name(ctx, name):
			return

		user_list = GIVEAWAY[name].get("user_in", None)
		if user_list is None:
			await send_message(ctx, f"GIVEAWAY: No user registred for giveaway **{name}**")
			return

		sanitized = list()
		guild_id = GIVEAWAY[name].get("id_guild", None)
		if guild_id is None:
			await send_message(ctx, f"GIVEAWAY: Giveaway **{name}**, not registred")
			return
		guild = self.bot.get_guild(guild_id)
		if guild is None:
			await send_message(ctx, f"GIVEAWAY: Giveaway **{name}**, guild id, {guild_id}, not found")
			return

		for user in user_list:
			if guild.get_member(user) is not None:
				sanitized.append(user)

		nb_user = len(sanitized)
		if nb_user == 0:
			await send_message(ctx, f"GIVEAWAY: No user registred for giveaway **{name}** :'(")
			return

		id_winner = sanitized[get_random_bytes(4) % nb_user]

		message = await send_message(ctx, "And the Winner is")
		time.sleep(1)
		await message.edit(content="And the Winner is .")
		time.sleep(1)
		await message.edit(content="And the Winner is ..")
		time.sleep(1)
		await message.edit(content="And the Winner is ...")
		time.sleep(1)
		message = await send_message(ctx, f"And the Winner is **<@{id_winner}>** ({id_winner})")

	@px_giveaway.command(
		name="list",
		description="List giveaway"
	)
	@discord.app_commands.describe(
		name = "The name of the giveaway, should be already created",
	)
	@discord.app_commands.autocomplete(
		name = px_autocomplete_giveaway_name
	)
	@is_allowed()
	async def giveaway_list(self, ctx, name: str = None):
		if not name:
			to_print = giveaway_list_all()
		elif name in GIVEAWAY:
			to_print = f"Giveaway details {name}" + giveaway_list_specific(name)
		else:
			await send_message(ctx, f"GIVEAWAY: No giveaway with name **{name}**")
			return

		await send_message(ctx, to_print)

	@px_giveaway.command(
		name="sync",
		description="Sync giveaways"
	)
	@is_allowed()
	async def giveaway_sync(self, ctx):
		if ctx.interaction:
			await ctx.interaction.response.defer()
		await giveaway_sync(self.bot)
		await send_message(ctx, f"Synchronised {len(GIVEAWAY)}")

	@px_giveaway.command(
		name="embed",
		description="Get an embed for giveaway"
	)
	@discord.app_commands.describe(
		title = "The title of the embed",
		desc = "The description of the embed",
	)
	@is_allowed()
	async def giveaway_embed(self, ctx, title: str = None, desc: str = None):
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

# UTILS
async def giveaway_check_name(ctx, name):
	if not name:
		await send_message(ctx, f"GIVEAWAY: Need a giveaway name")
		return True
	if not name in GIVEAWAY:
		await send_message(ctx, f"GIVEAWAY: No giveaway with name **{name}**")
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

async def	giveaway_get_message(channel, id):
	messages = [message async for message in channel.history(limit=500)]
	for m in messages:
		if m.id == id:
			return m

	return None

async def	giveaway_sync(bot):
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

def can_participate(user):
	if user["level"] < 2:
		return (False, "Need to be level 15 or higher")
	# if user["xp"] >= 1000:
	# 	return True
	return (True, None)

async def giveaway_can_join(payload, giveaway_id):
	return True

	html_json = get_mee6_leaderboard(payload.guild_id)
	html_json = json.loads(html_json)

	with open("mee6.json", "w") as f:
		f.write(json.dumps(html_json, indent=4))

	for user in html_json["players"]:
		if user["id"] == str(payload.user_id):
			retv, err = can_participate(user)
			if retv:
				print(f"{user['xp']:8d} (\x1b[32m{user['level']}\x1b[0m) {user['username']} ({user['id']})")
				return True
			else:
				print(f"{user['xp']:8d} (\x1b[31m{user['level']}\x1b[0m) {user['username']} ({user['id']})")
				await send_message(
					get_user(payload.user_id),
					f"**Failed** to join the giveaway id __{giveaway_id}__\nReason: {err}"
				)
				return False

def message_to_giveaway(id_message):
	for k, v in GIVEAWAY.items():
		if v.get("id_message") == id_message:
			return k
	return None
