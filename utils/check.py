from bot import discord
from bot import commands

from bot import get_author
from bot import send_message
from bot import ALLOWED_BRO

def is_bro(user):
	return user.id in ALLOWED_BRO

async def is_allowed_check(ctx):
	author = get_author(ctx)
	if isinstance(ctx, discord.Interaction):
		content = ctx.command.name
	elif isinstance(ctx, discord.ext.commands.Context):
		content = ctx.message.content

	if not is_bro(author):
		await send_message(ctx, "You are **not** an allowed bro ;)")
		print(
			f"not allowed bro {author.name} ({author.id}) tried:\n{content}"
		)
		return False
	return True

def is_allowed():
	return commands.check(is_allowed_check)

async def is_command_in_guild_check(ctx):
	return ctx.guild != None

def is_command_in_guild():
	return commands.check(is_command_in_guild_check)
