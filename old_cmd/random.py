import discord
from discord.ext import commands

from bot import bot
from bot import extended_check
from bot import random_fmt

@bot.command(
	name="random",
	description="Get a random number",
	check=extended_check,
)
async def random_cmd(ctx, *args):
    await random_fmt(ctx, *args)
