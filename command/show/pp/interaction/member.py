from bot import discord

from bot import bot
from bot import send_message
from bot import send_embed
from bot import get_embed

@bot.tree.context_menu(name="Show Profile Picture")
async def show_pp(interaction: discord.Interaction, member: discord.Member):
	embed = get_embed(interaction, f"{member}'s Profile picture")
	embed.set_image(url=member.avatar.url)
	await send_embed(interaction, embed)
