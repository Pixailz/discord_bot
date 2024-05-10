from bot import discord

from bot import bot
from bot import send_message

@bot.tree.context_menu(name="Show Join Date")
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
    await send_message(interaction, f"{member} joined at {discord.utils.format_dt(member.joined_at)}")
