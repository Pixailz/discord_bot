from bot import Union
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
		if user_giveaway_key is None:
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
		"u.id, ug.participate, ug.first_interaction",
		join= [
			("user u", "ug.user_key", "u.key"),
			("giveaway g", "ug.giveaway_key", "g.key"),
		],
		where = [("g.key", body[0])],
		col="participate",
		order="DESC"
	)

	nb_user = len(users)
	if nb_user > 0:
		s = "" if nb_user == 1 or nb_user == 0 else "s"
		fmt += f"\n{nb_user} User{s} found:\n"
		header = ["User Name", "User ID", "Participate", "First Interaction"]
		body = []

		for uid, participate, first_interaction in users:
			tmp = []
			tmp.append(str(get_user(uid)))
			tmp.append(uid)
			tmp.append('True' if participate else 'False')
			tmp.append(datetime.datetime.fromtimestamp(first_interaction).strftime("%d-%m-%Y %H:%M:%S"))
			body.append(tmp)
		fmt += f"```\n{t2a(header, body,
			style=t2aStyle.thin_compact_rounded,
			alignments=t2aAlignment.LEFT,
		)}\n```"
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
		from bot import pprint
		pprint(already_joined)
		for reaction in message.reactions:
			async for user in reaction.users():
				if not user.id in already_joined:
					await GiveawayCOG.giveaway_user_participate(
						user.id, message_id, True)
