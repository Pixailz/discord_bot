import json
import discord
import datetime
from discord.ext import commands

from bot import is_allowed
from bot import get_user

from pprint import pprint

async def dump_guild(ctx, arg_1):
	result = dict()

	if not arg_1 and not ctx.guild:
		await ctx.send("DUMP: Need a guild id")
		return
	if not arg_1:
		guild = ctx.guild
	else:
		guild = ctx.bot.get_guild(int(arg_1))
	if not guild:
		await ctx.send(f"DUMP: guild {arg_1} not found")
		return

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

	with open("dump.json", "w") as f:
		json.dump(result, f, indent=4)
	with open("dump.json", "r") as f:
		await ctx.send(f"Dumped server, {arg_1}", file=discord.File(f, "dump.json"))

async def dump_user(ctx, arg_1):
	if not arg_1:
		await ctx.send("DUMP: Need an user id")
		return

	user = get_user(arg_1)
	if not user:
		await ctx.send(f"DUMP: User id, {arg_1}, not found")
		return

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
	await ctx.send(f"```\n{to_print}\n```")

@commands.command()
@is_allowed()
async def dump(ctx, target: str, arg_1 = None):
	match target:
		case "guild":
			await dump_guild(ctx, arg_1)
		case "user":
			await dump_user(ctx, arg_1)
		case _:
			await ctx.send("Error, dump target not found")
			return
