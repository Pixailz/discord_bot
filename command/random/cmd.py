from bot import discord
from discord.ext import commands

from bot import bot
from bot import is_allowed
from bot import get_random_bytes
from bot import send_message

async def random_exec(
	ctx,
	length: int = 4,
	mod: int = 0,
	n: int = 1,
):
	ss = "" if length == 1 or length == 0 else "s"

	if mod != 0:
		to_print = f"{n} X ({length} random byte{ss} modulo {mod})"
	else:
		to_print = f"{n} X {length} random byte{ss}"

	to_print += ":"

	for i in range(0, n):
		to_print += f"\n- {get_random_bytes(length, mod)}"
	await send_message(ctx, to_print)

@bot.command(
	name="px_random",
	description="Get a random number",
)
@is_allowed()
async def random_cmd(ctx, *args):
    await random_exec(ctx, *args)
