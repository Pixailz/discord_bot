from bot import discord

from bot import bot
from bot import sync_exec
from bot import is_allowed

@bot.tree.command(
	name="px_sync",
)
@discord.app_commands.describe(
	subcmd = "Sub command to call",
	arg_1 = "First args to subcmd"
)
@is_allowed()
async def sync(
	ctx,
	subcmd: str,
	arg_1: str = None,
):
	await sync_exec(ctx, subcmd, arg_1)
