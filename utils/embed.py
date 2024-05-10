from bot import discord
from bot import datetime

from bot import get_author

def get_embed(ctx, title: str = "", desc: str = None, color: int = 0x00ff00):
	opt = {
		"title": title,
		"color": color,
		"timestamp": datetime.datetime.now(),
	}
	if desc != None:
		opt["description"] = desc
	author = get_author(ctx)
	embed = discord.Embed(**opt)
	embed.set_author(
		name=author.display_name,
		icon_url=author.display_avatar.url
	)
	return embed
