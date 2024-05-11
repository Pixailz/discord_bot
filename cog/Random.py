from bot import discord
from discord.ext import commands
from bot import Literal

from bot import is_allowed
from bot import send_message
from bot import get_random_bytes

class RandomCOG(
		commands.Cog,
		name="Random",
	):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		# print("Random cog loading")
		# print("------")
		# print("------")
		print("Random cog loaded")

	@commands.hybrid_command(
		name="px_random",
		description="Get a random number",
	)
	@discord.app_commands.describe(
		length = "Length, in byte(s), of the random number",
		mod = "Modulo for the result",
		n = "Number of random you want"
	)
	@is_allowed()
	async def px_random(self, ctx, length: int = 4, mod: int = 0, n: int = 1):
		ss = "" if length == 1 or length == 0 else "s"

		if mod != 0:
			to_print = f"{n} X ({length} random byte{ss} modulo {mod})"
		else:
			to_print = f"{n} X {length} random byte{ss}"

		to_print += ":"

		for i in range(0, n):
			to_print += f"\n- {get_random_bytes(length, mod)}"
		await send_message(ctx, to_print)
