import discord
from discord.ext import commands

from bot import is_allowed
from bot import get_user
from bot import IDS

@commands.command()
@is_allowed()
async def msg(ctx, target: str = None, msg: str = None):
	user = get_user(target)
	if not user:
		await ctx.send(f"MSG: User {target}, not found")
		return
	await ctx.send(f"Send to : <@{user.id}>\n```\n{msg}\n```")
	await user.send(f"Message delivery from <@{IDS['USER']['pix']}>:\n```\n{msg}\n```")
