from bot import discord
from discord.ext import commands

from bot import bot
from bot import datetime
from bot import send_message

def try_date_format(fmt, date_str):
	try:
		return datetime.datetime.strptime(date_str, fmt)
	except ValueError:
		return None

def get_ts(date_str):
	fmts = [
		"%d/%m/%y",
		"%d/%m/%Y",
		"%d/%m/%y %H:%M",
		"%d/%m/%Y %H:%M",
		"%d/%m/%y %H:%M:%S",
		"%d/%m/%Y %H:%M:%S",
	]
	ts = None
	for fmt in fmts:
		ts = try_date_format(fmt, date_str)
		if ts != None:
			ts = int(ts.timestamp())
			break
	return ts

async def date_exec(
		ctx,
		date_str: str = "01/01/1990 12:00:00",
		date_fmt:str = "f"
	):
	if date_str == "now":
		ts = int(datetime.datetime.now().timestamp())
	else:
		ts = get_ts(date_str)
	if ts == None:
		await send_message(ctx, f"{date_str} cannot be converted")
		return
	await send_message(ctx, f"<t:{ts}:{date_fmt}> -> `<t:{ts}:{date_fmt}>`")

@bot.command(
	name="px_date",
	description="Format a given, str date and convert if to Discord unviversal date",
)
async def date_cmd(ctx, *args):
    await date_exec(ctx, *args)
