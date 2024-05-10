from bot import discord

from bot import bot
from bot import send_message
from bot import get_user
from bot import message_to_giveaway
from bot import GIVEAWAY

@bot.event
async def on_raw_reaction_remove(payload):
	giveaway_id = message_to_giveaway(payload.message_id)
	if giveaway_id:
		if not "user_out" in GIVEAWAY[giveaway_id]:
			GIVEAWAY[giveaway_id]["user_out"] = list()
		if not "user_in" in GIVEAWAY[giveaway_id]:
			GIVEAWAY[giveaway_id]["user_in"] = list()

		if not payload.user_id in GIVEAWAY[giveaway_id]["user_out"]:
			GIVEAWAY[giveaway_id]["user_out"].append(payload.user_id)
		if payload.user_id in GIVEAWAY[giveaway_id]["user_in"]:
			GIVEAWAY[giveaway_id]["user_in"].remove(payload.user_id)

		print(f"GIVEAWAY: removed {payload.user_id} to {giveaway_id}")
		await send_message(
			get_user(payload.user_id),
			f"**Successfully** leaved the giveaway id __{giveaway_id}__",
		)
