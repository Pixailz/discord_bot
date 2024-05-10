import discord
from discord.ext import commands

from bot import is_allowed

@commands.command()
@is_allowed()
async def rm(ctx, username: str, limit: int = 100):
	if username.startswith("<@"):
		user_id = username[3:-1]
	else:
		member = ctx.guild.get_member_named(username)
		if member:
			user_id = member.id
		else:
			await ctx.send(f"User {username} not found")
			return

	deleted = 0
	await ctx.send(f"Deleting message from {username} ({user_id})")

	# Get the user
	for chan in ctx.guild.text_channels:
		async for message in chan.history(limit=limit):
			if message.author.id == user_id:
				await message.delete()
				print(deleted)
				deleted += 1

	await ctx.send(f"Deleted {deleted} messages from {username} ({user_id})")

