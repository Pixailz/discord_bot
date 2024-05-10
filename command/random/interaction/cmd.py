from bot import discord

from bot import bot
from bot import random_exec
from bot import extended_check

@bot.tree.command(
	name="px_random",
	description="Get a random number"
)
@discord.app_commands.describe(
	length = "Length, in byte(s), of the random number",
	mod = "Modulo for the result",
	n = "Number of random you want"
)
async def random(
	interaction,
	length: int = 4,
	mod: int = 0,
	n: int = 1,
):
	if await extended_check(interaction):
		return
	await random_exec(interaction, length, mod, n)
