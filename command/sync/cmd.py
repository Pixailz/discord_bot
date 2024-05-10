from bot import time
from bot import discord
from discord.ext import commands

from bot import bot
from bot import is_allowed
from bot import send_message
from bot import TO_SYNC

async def sync_cmd_tree(ctx):
	print("------")
	print("Syncing tree")
	for guild in TO_SYNC:
		guild_o = discord.Object(id=guild)  # replace with your guild id
		bot.tree.copy_global_to(guild=guild_o)
		print(f"Synced tree to guild {guild_o.id}")
	await bot.tree.sync()
	print("Synced tree")
	print("------")
	await send_message(ctx, "Synced cmd tree")

async def sync_exec(ctx, cmd: str, *args: str):
	match cmd:
		case "cmd_tree":
			await sync_cmd_tree(ctx)
		case _:
			await send_message(ctx, f"SYNC: cmd {cmd} not found")

@bot.command(
	name="px_sync",
	description="Sync thing",
	usage="cmd_tree",
)
@is_allowed()
async def sync_cmd(ctx, cmd: str, *args: str):
	await sync_exec(ctx, cmd, *args)
