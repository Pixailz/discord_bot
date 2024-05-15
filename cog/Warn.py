from bot import discord
from bot import datetime

from discord.ext import commands

from bot import is_command_in_guild
from bot import send_message
from bot import WARN
from bot import print_user

class WarnCOG(
		commands.Cog,
		name="Warn",
	):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		# print("Warn cog loading")
		# print("------")
		# print("------")
		print("Warn cog loaded")

	@commands.hybrid_group(name="px_warn", description="Warn someone about something")
	async def px_warn(self, ctx):
		pass

	@px_warn.command(
		name="user",
		description="Warn someone about something"
	)
	@discord.app_commands.describe(
		user = "The user to warn",
		reason = "The reason the user is warned",
	)
	@commands.has_permissions(administrator = True)
	@is_command_in_guild()
	async def warn_user(self, ctx,
		user: discord.User,
		reason: str,
	):
		await warn_user(ctx, user, reason)

	@px_warn.command(
		name="list",
		description="List warn about someone or all"
	)
	@discord.app_commands.describe(
		user = "List warn of a user",
	)
	@is_command_in_guild()
	@commands.has_permissions(administrator = True)
	async def warn_list(self, ctx,
		user: discord.User = None,
	):
		if user is None:
			await send_message(ctx, "TODO")
		else:
			guild_id = str(ctx.guild.id)
			guild_warn = WARN.get(guild_id, None)
			if guild_warn is None:
				await send_message(ctx, "No warn found for this guild")
			else:
				await send_message(ctx, get_warn_user(user, WARN[guild_id]))

async def warn_user(ctx, user: discord.User = None, reason: str = None):
	if reason is None or not len(reason):
		await send_message(ctx, "Reason **should** be given")
		return

	warn = {
		"occured_at":	int(datetime.datetime.now().timestamp()),
		"reason":		reason,
	}

	guild_id = str(ctx.message.guild.id)
	guild_warn = WARN.get(guild_id, None)

	if guild_warn is None:
		WARN[guild_id] = dict()
		guild_warn = WARN[guild_id]

	user_id = str(user.id)
	if user_id in guild_warn.keys():
		WARN[guild_id][user_id].append(warn)
	else:
		WARN[guild_id][user_id] = [ warn ]

	print(f"Warned {print_user(user.id)} {reason}")
	await send_message(ctx, f"{user.mention} have been warned: **{reason}**")

def get_warn(warn):
	return f"<t:{warn['occured_at']}:R>: **{warn['reason']}**"

def get_warns(warns):
	ret = ""
	for warn in warns:
		ret += f"- {get_warn(warn)}\n"
	return ret

def get_warn_user(user, guild_warn):
	user_id = str(user.id)
	if not user_id in guild_warn:
		return "No warn found for " + print_user(user.id)

	warns = guild_warn[user_id]
	return f"Found {len(warns)} for {print_user(user.id)}:\n" + get_warns(warns)
