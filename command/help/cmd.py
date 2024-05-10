from bot import discord
from discord.ext import commands

from bot import extended_check

class CustomHelp(commands.MinimalHelpCommand):
	async def send_pages(self):
		destination = self.get_destination()
		for page in self.paginator.pages:
			emby = discord.Embed(description=page)
			await destination.send(embed=emby)

	# !help
	async def send_bot_help(self, mapping):
		if await extended_check(self.context):
			await super().send_bot_help(mapping)

	# !help <command>
	async def send_command_help(self, command):
		if await extended_check(self.context):
			await super().send_command_help(command)

	# !help <group>
	async def send_group_help(self, group):
		if await extended_check(self.context):
			await super().send_group_help(group)

	# !help <cog>
	async def send_cog_help(self, cog):
		if await extended_check(self.context):
			await super().send_cog_help(cog)
