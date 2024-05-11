from bot import discord
from bot import datetime
from bot import Literal

from discord.ext import commands

from bot import is_allowed
from bot import send_message

fmts_in = [
	discord.app_commands.Choice(
		name="INTL: Date (%d/%m/%Y)",
		value="%d/%m/%Y"
	),
	discord.app_commands.Choice(
		name="US: Date (%m/%d/%Y)",
		value="%m/%d/%Y"
	),

	discord.app_commands.Choice(
		name="INTL: Date Short Time(%d/%m/%Y %H:%M)",
		value="%d/%m/%Y %H:%M"
	),
	discord.app_commands.Choice(
		name="US: Date Short Time(%m/%d/%Y %H:%M %p)",
		value="%m/%d/%Y %H:%M %p"
	),

	discord.app_commands.Choice(
		name="INTL: Date Long time (%d/%m/%Y %H:%M:%S)",
		value="%d/%m/%Y %H:%M:%S"
	),
	discord.app_commands.Choice(
		name="US: Date Long time (%m/%d/%Y %H:%M:%S %p)",
		value="%m/%d/%Y %H:%M:%S %p"
	),

	discord.app_commands.Choice(
		name="INTL: Date Very long time (%d/%m/%Y %H:%M:%S%z)",
		value="%d/%m/%Y %H:%M:%S%z"
	),
	discord.app_commands.Choice(
		name="US: Date Very long time (%m/%d/%Y %H:%M:%S%z %p)",
		value="%m/%d/%Y %H:%M:%S%z %p"
	),
]

fmts_out = [
	discord.app_commands.Choice(
		name="Default (None)",
		value="",
	),
	discord.app_commands.Choice(
		name="Short Time (t)",
		value="t",
	),
	discord.app_commands.Choice(
		name="Long Time (T)",
		value="T",
	),
	discord.app_commands.Choice(
		name="Short Date (d)",
		value="d",
	),
	discord.app_commands.Choice(
		name="Long Date (D)",
		value="D",
	),
	discord.app_commands.Choice(
		name="Short Date/Time (f)",
		value="f",
	),
	discord.app_commands.Choice(
		name="Long Date/Time (t)",
		value="F",
	),
	discord.app_commands.Choice(
		name="Relative Time (R)",
		value="R",
	),
]

async def px_date_fmt_in(ctx, current: str):
	if len(current) == 0:
		return fmts_in
	result = list()
	for fmt in fmts_in:
		if fmt.name.startswith(current) or fmt.value.startswith(current):
			result.append(fmt)

	if len(result) > 0:
		return result

	return [discord.app_commands.Choice(
		name = f"Custom ({current})",
		value = current
	),]

class DateCOG(
		commands.Cog,
		name="Date",
	):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		# print("Date cog loading")
		# print("------")
		# print("------")
		print("Date cog loaded")

	@commands.hybrid_command(
		name="px_date",
		description="Format a date and convert it to Discord unviversal date",
	)
	@discord.app_commands.describe(
		date = "The date",
		fmt_in = "The input format",
		fmt_out = "The output format",
	)
	@discord.app_commands.choices(
		fmt_out = fmts_out
	)
	@discord.app_commands.autocomplete(
		fmt_in = px_date_fmt_in
	)
	@is_allowed()
	async def px_date(self, ctx,
		date: str = "now",
		fmt_in: str = "%d/%m/%Y",
		fmt_out: str = "F",
	):
		if date == "now":
			ts = datetime.datetime.now()
		else:
			ts = try_get_datetime(fmt_in, date)
			if ts == None:
				await send_message(ctx, f"{date} cannot be converted from {fmt_in}")
				return

		ts = int(ts.timestamp())
		await send_message(ctx, f"<t:{ts}:{fmt_out}> -> `<t:{ts}:{fmt_out}>`")

def try_get_datetime(fmt, date):
	try:
		return datetime.datetime.strptime(date, fmt)
	except ValueError:
		return None
