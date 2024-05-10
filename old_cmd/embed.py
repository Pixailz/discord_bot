import datetime
import discord
from discord.ext import commands

from bot import is_allowed

def get_embed(ctx, title: str = "", desc: str = "", color: int = 0x00ff00):
	embed = discord.Embed(
		title=title,
		description=desc,
		color=color,
		timestamp=datetime.datetime.now()
	)
	embed.set_author(
		name=ctx.author.display_name,
		icon_url=ctx.author.display_avatar.url
	)
	return embed

# async def embed_test(ctx, title, desc):
# 	title = title or "GIVEAWAY"
# 	desc = desc or "This is a giveaway"
# 	embed = get_embed(ctx, f"🎊 {title} 🎊", desc)
# 	embed.add_field(name="How to join", value="Just react to this message and you will greated with a message once joined")
# 	embed.set_footer(text="by Pixailz")
# 	await ctx.send(embed=embed)

@commands.command()
@is_allowed()
async def embed(ctx, target: str, arg_1: str = None, arg_2: str = None):
	match target:
		case "giveaway":
			await embed_giveaway(ctx, arg_1, arg_2)
		case "test":
			await embed_test(ctx, arg_1, arg_2)
		case _:
			await ctx.send("Error, embed not found")
			return
