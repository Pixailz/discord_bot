from bot import discord

from bot import bot
from bot import date_exec

@bot.tree.command(
	name="px_date",
	description="Format a given, str date and convert if to Discord unviversal date"
)
@discord.app_commands.describe(
	date = "The Date to format",
)
async def date(
	ctx,
	date: str,
):
	await date_exec(ctx, date)
