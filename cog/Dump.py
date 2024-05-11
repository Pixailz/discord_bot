from bot import json
from bot import Union
from bot import discord
from discord.ext import commands

from bot import is_allowed
from bot import send_message

class DumpCOG(
		commands.Cog,
		name="Dump",
	):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.dump_user = discord.app_commands.ContextMenu(
			name='Dump member / user',
			callback=self.dump_member_exec,
		)

		self.bot.tree.add_command(self.dump_user)

	# EVENT
	@commands.Cog.listener()
	async def on_ready(self):
		# print("Dump cog loading")
		# print("------")
		# print("------")
		print("Dump cog loaded")

	@commands.hybrid_group(name="px_dump", description="Dump everything")
	async def px_dump(self, ctx):
		pass

	@px_dump.command(
		name="guild",
		description="Dump a guild"
	)
	@discord.app_commands.describe(
		guild = "The guild to be dumped",
	)
	@is_allowed()
	async def dump_guild(self, ctx, guild: discord.Guild):
		if guild is None:
			await send_message(ctx, f"Wrong guild {guild}")
			return

		result = dict()
		result["name"] = guild.name
		result["id"] = guild.id
		result["member_count"] = guild.member_count
		result["banner"] = guild.banner
		result["description"] = guild.description
		result["created_at"] = guild.created_at.strftime("%d/%m/%y %H:%M:%S")
		result["owner"] = guild.owner.display_name
		result["owner_id"] = guild.owner.id

		result["members"] = list()
		for member in guild.members:
			result["members"].append({
				"display_name": member.display_name,
				"id": member.id,
				"created_at": member.created_at.strftime("%d/%m/%y %H:%M:%S")
			})

		result["category"] = list()
		result["channels"] = list()
		for channel in guild.channels:
			if channel.type[0] != "category":
				tmp = {
					"type": channel.type[0],
					"name": channel.name,
					"id": channel.id,
					"created_at": channel.created_at.strftime("%d/%m/%y %H:%M:%S"),
					"position": channel.position,
				}
				if channel.category:
					tmp["category"] = channel.category.id
				result["channels"].append(tmp)
			else:
				tmp = {
					"name": channel.name,
					"id": channel.id,
					"created_at": channel.created_at.strftime("%d/%m/%y %H:%M:%S"),
					"position": channel.position,
				}
				result["category"].append(tmp)

		await send_message(ctx,
			"```json\n" + json.dumps(result, indent=4) + "```"
		)

	@px_dump.command(
		name="user",
		description="Dump an user"
	)
	@discord.app_commands.describe(
		user = "The user to be dumped",
	)
	@is_allowed()
	async def dump_member(self, ctx, user: Union[discord.Member, discord.User]):
		await self.dump_member_exec(ctx, user)

	async def dump_member_exec(self, ctx, user: Union[discord.Member, discord.User]):
		to_print = f"User {user.display_name} ({user.id})\n"
		if getattr(user, "accent_color", None):
			to_print += f"  - accent_color: {hex(user.accent_color.value)}\n"
		if getattr(user, "avatar", None):
			to_print += f"  - avatar: {user.avatar.url}\n"
		if getattr(user, "banner", None):
			to_print += f"  - banner: {user.banner.url}\n"
		to_print += f"  - bot: {user.bot}\n"
		if getattr(user, "color", None):
			to_print += f"  - color: {hex(user.color.value)}\n"
		to_print += f"  - created_at: {user.created_at.timestamp()}\n"
		if getattr(user, "default_avatar", None):
			to_print += f"  - default_avatar: {user.default_avatar.url}\n"
		to_print += f"  - discriminator: {user.discriminator}\n"
		to_print += f"  - global_name: {user.global_name}\n"
		to_print += f"  - id: {user.id}\n"
		to_print += f"  - public_flags: {user.public_flags}\n"
		to_print += f"  - system: {user.system}\n"
		await send_message(ctx, f"Dumped user {user.name}\n```\n{to_print}\n```")

# UTILS
