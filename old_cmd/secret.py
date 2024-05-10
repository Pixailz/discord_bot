import subprocess

import discord
from discord.ext import commands

from bot import is_allowed

@commands.command()
@is_allowed()
async def secret(ctx):
	proc = subprocess.run(["whoami"], stdout=subprocess.PIPE)

	await ctx.send(proc.stdout.decode("utf-8"))
