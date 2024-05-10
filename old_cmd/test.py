import discord
from discord.ext import commands

from bot import is_allowed

@commands.command()
@is_allowed()
async def test(ctx):
	await ctx.send("tested")
