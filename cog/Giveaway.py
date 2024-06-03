from bot import Union
from bot import time
from bot import datetime
from bot import discord
from discord.ext import commands
from bot import Literal

from bot import main_db
from bot import NameTable
from bot import t2a, t2aStyle, t2aAlignment

from bot import get_embed
from bot import print_user
from bot import is_allowed
from bot import send_message
from bot import send_embed
from bot import get_mee6_leaderboard
from bot import get_random_bytes
from bot import get_user
from bot import print_user

from bot import pprint

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

	@staticmethod
	def on_reaction_get_user(user_id, message_id):
		retv, value = main_db.cget_user_giveaway(user_id, message_id)
		if not retv:
			err_msg = f"Failed register {print_user(user_id)}\n"
			err_msg += f"> Reason: {value}"
			print(err_msg)
			return None
		return value

	@staticmethod
	async def on_reaction_send_status(user_id, message_id, verb):
		user = get_user(user_id)
		ga_key = main_db.get_giveaway_key(message_id)
		ga_name = main_db.get_one(NameTable.giveaway, "name", [("key", ga_key)])
		ga_name = ga_name[0]
		await send_message(user,
			f"{print_user(user)} **{verb}** giveaway __{ga_name}__ (**{ga_key}**)"
		)

	@staticmethod
	async def giveaway_user_participate(user_id, message_id, participate):
		user_giveaway_key = GiveawayCOG.on_reaction_get_user(user_id, message_id)
		if user_giveaway_key is None and giveaway_can_join(user_id, message_id) is False:
			return

		main_db.update(NameTable.user_giveaway,
			[("participate", participate)],
			[("key", user_giveaway_key)]
		)
		verb = "joined" if participate else "leaved"
		await GiveawayCOG.on_reaction_send_status(user_id, message_id, verb)

	@commands.Cog.listener()
	async def on_raw_reaction_add(self,
			payload: discord.RawReactionActionEvent
		):
		await GiveawayCOG.giveaway_user_participate(
			payload.user_id, payload.message_id, True)

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		await GiveawayCOG.giveaway_user_participate(
			payload.user_id, payload.message_id, False)

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
		retv, giveaway_key = main_db.cget_giveaway(name)
		if not retv:
			await send_message(ctx, "Failed to create giveaway")
			return

		await send_message(ctx, f"Giveaway {name} created with id {giveaway_key}")

	@px_giveaway.command(
		name="register",
		description="Register a giveaway, given a giveaway id and a message"
	)
	@discord.app_commands.describe(
		giveaway_key = "The id of the giveaway, should be already created",
		message = "The message of the giveaway, should be in a guild",
	)
	@is_allowed()
	async def giveaway_register(self, ctx,
		giveaway_key: int,
		message: discord.Message,
	):
		if main_db.get_one(NameTable.giveaway, "key", [("key", giveaway_key)]) is None:
			await send_message(ctx, f"Giveaway {giveaway_key} not found")
			return

		if message is None:
			await send_message(ctx, "Message not found")
			return

		if getattr(message, "guild", None) is None:
			await send_message(ctx, "Message should be in a guild")
			return

		if main_db.register_giveaway_message(giveaway_key, message):
			await send_message(ctx,
				f"Giveaway {giveaway_key} successfully registered {message.id}"
			)
		else:
			await send_message(ctx, "Failed to register giveaway")

	@px_giveaway.command(
		name="list",
		description="List giveaway"
	)
	@discord.app_commands.describe(
		giveaway_key = "The id of the giveaway, should be already created",
	)
	@is_allowed()
	async def giveaway_list(self, ctx, giveaway_key: int = None):
		if giveaway_key is None:
			await self.giveaway_list_all(ctx)
			return

		await self.giveaway_list_one(ctx, giveaway_key)

	async def giveaway_list_one(self, ctx, giveaway_key: int):
		giveaway = main_db.get_one(NameTable.giveaway, "*", [
			("key", giveaway_key)
		])
		if giveaway is None:
			await send_message(ctx, f"No giveaway found with key {giveaway_key}")
			return
		await send_message(ctx, fmt_db_giveaway_one(giveaway))

	async def giveaway_list_all(self, ctx):
		giveaways = main_db.get(
			NameTable.giveaway,
			select="key, name, created, message_key",
			col="key"
		)
		if giveaways is None:
			await send_message(ctx, "No giveaway found")
			return

		header = ["Key", "Name", "Created", "Message ID", "Participant"]
		body = []

		for giveaway in giveaways:
			body.append(fmt_db_giveaway_all(giveaway))

		fmt = t2a(header, body,
			style=t2aStyle.thin_compact_rounded,
			first_col_heading=True,
			alignments=t2aAlignment.LEFT,
		)
		await send_message(ctx, f"```\n{fmt}\n```")

	@px_giveaway.command(
		name="winner",
		description="Get a winner, given a giveaway key"
	)
	@discord.app_commands.describe(
		giveaway_key = "The id of the giveaway, should be already created",
	)
	@is_allowed()
	async def giveaway_winner(self, ctx, giveaway_key):
		giveaway = main_db.get_one(f"{NameTable.giveaway} ga",
			"ga.key, ga.name, guild.id",
			[("ga.key", giveaway_key)],
			join = [
				("channel", "message_key", "ga.key"),
				("guild", "channel.guild_key", "channel.key"),
			]
		)
		if giveaway is None:
			await send_message(ctx,
				f"Giveaway {giveaway_key} not found, or not registred"
			)
			return
		giveaway_key = giveaway[0]
		giveaway_name = giveaway[1]
		giveaway_guild = giveaway[2]

		user_list = main_db.get(f"{NameTable.user_giveaway} ug",
			"user.id, user.key",
			join= [
				("user", "ug.user_key", "user.key"),
				("giveaway", "ug.giveaway_key", "giveaway.key"),
			],
			where = [
				("giveaway.key", giveaway_key),
				("ug.participate", True),
				("ug.has_win", False)
			]
		)

		if len(user_list) == 0:
			await send_message(ctx, f"No user found for giveaway `{giveaway_name}`")
			return

		sanitized = list()
		guild = self.bot.get_guild(giveaway_guild)
		if guild is None:
			await send_message(ctx, f"guild id, {guild_id}, not found")
			return

		for user in user_list:
			if guild.get_member(user[0]) is not None:
				sanitized.append(user)

		nb_user = len(sanitized)
		if nb_user == 0:
			await send_message(ctx, f"No user found for giveaway `{giveaway_name}`")
			return

		winner = sanitized[get_random_bytes(4) % nb_user]
		print(f"{giveaway_key = }")
		winner_id = main_db.get(
			NameTable.user_giveaway, "*", [
				("giveaway_key", giveaway_key),
				("NE", "has_win", 0)
			]
		)
		if winner_id == None:
			winner_id = 1
		else:
			winner_id = len(winner_id) + 1
		main_db.update(NameTable.user_giveaway, [("has_win", winner_id)],
			[("giveaway_key", giveaway_key), ("user_key", winner[1])]
		)

		message = await send_message(ctx, "And the Winner is")
		time.sleep(1)
		await message.edit(content="And the Winner is .")
		time.sleep(1)
		await message.edit(content="And the Winner is ..")
		time.sleep(1)
		await message.edit(content="And the Winner is ...")
		time.sleep(1)
		message = await send_message(ctx, f"And the Winner is **<@{winner[0]}>** ({winner[0]})")

	@px_giveaway.command(
		name="sync",
		description="Sync giveaways"
	)
	@is_allowed()
	async def giveaway_sync(self, ctx):
		if ctx.interaction:
			await ctx.interaction.response.defer()
		await giveaway_sync(self.bot)
		await send_message(ctx, f"Synchronised Giveaways")

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

def fmt_db_giveaway_all(ga):
	body = []
	body.append(ga[0])
	body.append(ga[1])
	body.append(datetime.datetime.fromtimestamp(ga[2]).strftime("%d-%m-%Y %H:%M:%S"))
	body.append(None)
	body.append(None)

	if ga[3] is not None:
		message_id = main_db.get_one(NameTable.message, "id", [("key", ga[3])])
		body[3] = message_id[0]
		body[4] = len(main_db.get(f"{NameTable.user_giveaway} ug",
			"u.id, ug.participate, ug.first_interaction",
			join= [
				("user u", "ug.user_key", "u.key"),
				("giveaway g", "ug.giveaway_key", "g.key"),
			],
			where = [
				("g.key", body[0]),
				("ug.participate", True),
			],
		))
	return (body)

def fmt_db_giveaway_one(ga):
	body = fmt_db_giveaway_all(ga)
	fmt = f"Giveaway details for key **{body[0]}**:\n"
	fmt += f"- Name: `{body[1]}`\n"
	fmt += f"- Created: `{body[2]}`\n"
	if body[3] is not None:
		fmt += f"- Message ID: `{body[3]}`\n"

	users = main_db.get(f"{NameTable.user_giveaway} ug",
		"u.id, ug.participate, ug.first_interaction, ug.has_win",
		join= [
			("user u", "ug.user_key", "u.key"),
			("giveaway g", "ug.giveaway_key", "g.key"),
		],
		where = [("g.key", body[0])],
		col="participate, has_win",
	)

	nb_user = len(users)
	if nb_user > 0:
		s = "" if nb_user == 1 or nb_user == 0 else "s"
		fmt += f"\n{nb_user} User{s} found:\n"
		header = ["User Name", "User ID", "IsIn", "First Interaction", "WinID"]
		body = []

		for uid, participate, first_interaction, win_id in users:
			tmp = []
			tmp.append(str(get_user(uid)))
			tmp.append(uid)
			tmp.append('True' if participate else 'False')
			tmp.append(datetime.datetime.fromtimestamp(first_interaction).strftime("%d-%m-%Y %H:%M:%S"))
			tmp.append(win_id)
			body.append(tmp)

		fmt += f"""```\n{t2a(header, body,
			style=t2aStyle.thin_compact_rounded,
			alignments=t2aAlignment.LEFT,
		)}\n```"""
	else:
		fmt += "No user found for this giveaway"

	return fmt

async def	giveaway_get_message(channel, id):
	messages = [message async for message in channel.history(limit=500)]
	for m in messages:
		if m.id == id:
			return m

	return None

async def	giveaway_sync(bot):
	giveaways = main_db.get(
		f"{NameTable.giveaway} ga",
		"ga.key, ga.name, m.id, c.id, gu.id",
		join=[
			("message m", "ga.message_key", "m.key"),
			("channel c", "m.channel_key", "c.key"),
			("guild gu", "c.guild_key", "gu.key")
		]
	)
	if giveaways == None:
		print("No giveaways to synchronise")
		return

	for giveaway_key, giveaway_name, message_id, channel_id, guild_id in giveaways:
		channel = bot.get_guild(guild_id).get_channel(channel_id)
		message = await giveaway_get_message(channel, message_id)
		if not message:
			print(
				f"Message ({message_id}) not found for"
				f"giveaway {giveaway_name} ({giveaway_key})"
			)
			continue

		users = main_db.get(f"{NameTable.user_giveaway} ug", "u.id",
			join= [
				("user u", "ug.user_key", "u.key"),
				("giveaway g", "ug.giveaway_key", "g.key"),
			],
			where = [
				("g.key", giveaway_key),
				("ug.participate", True)
			],
		)
		already_joined = [ u[0] for u in users ]
		for reaction in message.reactions:
			async for user in reaction.users():
				if not user.id in already_joined:
					await GiveawayCOG.giveaway_user_participate(
						user.id, message_id, True)

	print("Synchronised giveaways")

def can_participate(user):
	if user["level"] < 2:
		return (False, "Need to be level 2 or higher")
	# if user["xp"] >= 1000:
	# 	return True
	return (True, None)

async def giveaway_can_join(payload, giveaway_id):
	try:
		html_json = get_mee6_leaderboard(payload.guild_id)
		html_json = json.loads(html_json)
	except Exception as e:
		print(f"Failed to get leaderboard: {e}")
		return True

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
