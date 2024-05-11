from bot import discord

from bot import bot
from bot import ENV

@bot.event
async def on_ready():
	print(f'Bot logged in as {bot.user} (ID: {bot.user.id})')
	print("------")
	print(discord.utils.oauth_url(ENV["DISCORD_CLIENT_ID"]))
	print("------")

	print("Available command")
	for command in bot.commands:
		print(f"  - {command.name}")
	print("------")
