from bot import discord
from bot import commands

from bot import get_author
from bot import ALLOWED_BRO

def is_bro(user):
	return user.id in ALLOWED_BRO

async def extended_check(ctx):
	author = get_author(ctx)
	print(f"{author} checked")
	if isinstance(ctx, discord.Interaction):
		content = interaction.command.name
	elif isinstance(ctx, discord.ext.commands.Context):
		content = ctx.message.content

	if not is_bro(author):
		await send_message(
			"You are **not** an allowed bro ;)", ephemeral=True)
		print(
			f"not allowed bro {author.name} ({author.id}) tried:\n{content}"
		)
		return False
	return True

def is_allowed():
	return commands.check(extended_check)
