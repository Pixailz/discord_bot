from bot import discord

from bot import bot
from bot import spam_exec
from bot import extended_check

@bot.tree.command(
	name="px_spam",
	description="Spam an user or a channel"
)
@discord.app_commands.describe(
	target = "The user or channel",
	msg = "The message to spam",
	time = "Time between message",
	nb = "Number of message to send",
)
async def spam(
	interaction,
	target: discord.User,
	msg: str,
	time: float = 1.0,
	nb: int = 10,
):
	if await extended_check(interaction):
		return
	await spam_exec(interaction, target, msg, time, nb)
