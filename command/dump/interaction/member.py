from bot import Union
from bot import discord

from bot import bot
from bot import spam_exec
from bot import send_message

@bot.tree.context_menu(name='Dump member / user')
async def dump_member(interaction, member: Union[discord.Member, discord.User]):
	to_print = f"User {member.display_name} ({member.id})\n"
	if getattr(member, "accent_color", None):
		to_print += f"  - accent_color: {hex(member.accent_color.value)}\n"
	if getattr(member, "avatar", None):
		to_print += f"  - avatar: {member.avatar.url}\n"
	if getattr(member, "banner", None):
		to_print += f"  - banner: {member.banner.url}\n"
	to_print += f"  - bot: {member.bot}\n"
	if getattr(member, "color", None):
		to_print += f"  - color: {hex(member.color.value)}\n"
	to_print += f"  - created_at: {member.created_at.timestamp()}\n"
	if getattr(member, "default_avatar", None):
		to_print += f"  - default_avatar: {member.default_avatar.url}\n"
	to_print += f"  - discriminator: {member.discriminator}\n"
	to_print += f"  - global_name: {member.global_name}\n"
	to_print += f"  - id: {member.id}\n"
	to_print += f"  - public_flags: {member.public_flags}\n"
	to_print += f"  - system: {member.system}\n"
	await send_message(interaction, f"Dumped member {member.name}\n```\n{to_print}\n```")
