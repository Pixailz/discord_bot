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

class GiveawayCOG(
		commands.Cog,
		name="Giveaway",
	):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	# EVENT
	@commands.Cog.listener()
	async def on_ready(self):
		# print("Giveaway cog loading")
		# print("------")
		# print("------")
		print("Giveaway cog loaded")

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		pass

	@commands.Cog.listener()
	async def on_raw_reaction_remove(self, payload):
		pass

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
		retv, giveaway_key = main_db.create_giveaway(name)
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

		from bot import pprint

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
		await send_message(ctx, f"```\n{fmt_db_giveaway_one(giveaway)}\n```")

	async def giveaway_list_all(self, ctx):
		giveaways = main_db.get(
			NameTable.giveaway,
			select="key, name, created, message_key",
			col="key"
		)
		if giveaways is None:
			await send_message(ctx, "No giveaway found")
			return

		header = ["Key", "Name", "Created", "Message Key", "Message ID"]
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
		body[3] = ga[3]
		message_id = main_db.get_one(NameTable.message, "id", [("key", ga[3])])
		body[4] = message_id[0]
	return (body)

def fmt_db_giveaway_one(ga):
	body = fmt_db_giveaway_all(ga)
	fmt = f"Giveaway details for key **{body[0]}**:\n"
	fmt += f"- Name: `{body[1]}`\n"
	fmt += f"- Created: `{body[2]}`\n"
	if body[3] is not None:
		fmt += f"- Message Key: `{body[3]}`\n"
		fmt += f"- Message ID: `{body[4]}`\n"
	return fmt
