from bot import sleep
from bot import discord
from discord.ext import commands

from bot import bot
from bot import is_allowed
from bot import send_message
from bot import get_user
from bot import get_author

from bot import pprint

async def spam_one(ctx, user, user_from, info_msg, msg, i, nb):
	await send_message(user, f"spammed by <@{user_from.id}>:\n```\n{msg}\n```")
	if isinstance(ctx, discord.Interaction):
		await ctx.edit_original_response(content=f"SPAM: User {user} found, sending msg ({i}/{nb})")
	elif isinstance(ctx, discord.ext.commands.Context):
		await info_msg.edit(content=f"SPAM: User {user} found, sending msg ({i}/{nb})")

async def spam_exec(
		ctx,
		target: str,
		msg: str,
		time: float = 1.0,
		nb: int = 10,
	):
	user = get_user(target)
	if not user:
		await send_message(ctx, f"SPAM: User {target}, not found")
		return
	info_msg = await send_message(ctx, f"SPAM: User {user} found, sending msg (0/{nb})")
	time = float(time)
	user_from = get_author(ctx)
	await spam_one(ctx, user, user_from, info_msg, msg, 1, nb)
	for i in range(2, nb + 1):
		await sleep(time)
		await spam_one(ctx, user, user_from, info_msg, msg, i, nb)

@bot.command(
	name="px_spam",
	description="Spam an user or a guild",
)
@is_allowed()
async def spam_cmd(ctx, *args):
    await spam_exec(ctx, *args)
