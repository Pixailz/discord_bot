from bot import discord
from discord.ext import commands

from bot import send_message
from bot import is_allowed
from bot import IDS

class SyncCOG(
		commands.Cog,
		name="Sync",
	):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	# EVENT
	@commands.Cog.listener()
	async def on_ready(self):
		# print("Sync cog loading")
		# print("------")
		# print("------")
		print("Sync cog loaded")

	@commands.hybrid_group(name="px_sync", description="Sync anything")
	async def px_sync(self, ctx):
		pass

	@px_sync.command(
		name="cmd_tree",
		description="Sync cmd tree"
	)
	@is_allowed()
	async def sync_cmd_tree(self, ctx):
		if ctx.interaction:
			await ctx.interaction.response.defer()
		print("------")
		print("Syncing tree")
		for guild_name, guild_id in IDS["GUILD"].items():
			guild_o = discord.Object(id=guild_id)
			self.bot.tree.copy_global_to(guild=guild_o)
			print(f"Synced tree to guild {guild_name} ({guild_id})")
		await self.bot.tree.sync()
		print("Synced tree")
		print("------")
		await send_message(ctx, "Synced cmd tree")

# UTILS
