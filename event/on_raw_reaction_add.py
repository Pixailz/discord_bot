from bot import discord
from bot import json
from bot import urllib
from bot import Request

from bot import bot
from bot import get_user
from bot import send_message
from bot import message_to_giveaway
from bot import get_mee6_leaderboard
from bot import GIVEAWAY
from bot import ENV

def can_participate(user):
	if user["level"] < 2:
		return (False, "Need to be level 15 or higher")
	# if user["xp"] >= 1000:
	# 	return True
	return (True, None)

async def can_join_giveaway(payload, giveaway_id):
	return True

	html_json = get_mee6_leaderboard(payload.guild_id)
	html_json = json.loads(html_json)

	with open("mee6.json", "w") as f:
		f.write(json.dumps(html_json, indent=4))

	for user in html_json["players"]:
		if user["id"] == str(payload.user_id):
			retv, err = can_participate(user)
			if retv:
				print(f"{user['xp']:8d} (\x1b[32m{user['level']}\x1b[0m) {user['username']} ({user['id']})")
				return True
			else:
				print(f"{user['xp']:8d} (\x1b[31m{user['level']}\x1b[0m) {user['username']} ({user['id']})")
				await send_message(
					get_user(payload.user_id),
					f"**Failed** to join the giveaway id __{giveaway_id}__\nReason: {err}"
				)
				return False

@bot.event
async def on_raw_reaction_add(payload):
	giveaway_id = message_to_giveaway(payload.message_id)
	if giveaway_id and await can_join_giveaway(payload, giveaway_id):
		if not "user_in" in GIVEAWAY[giveaway_id]:
			GIVEAWAY[giveaway_id]["user_in"] = list()
		if not "user_out" in GIVEAWAY[giveaway_id]:
			GIVEAWAY[giveaway_id]["user_out"] = list()

		if not payload.user_id in GIVEAWAY[giveaway_id]["user_in"]:
			GIVEAWAY[giveaway_id]["user_in"].append(payload.user_id)
		if payload.user_id in GIVEAWAY[giveaway_id]["user_out"]:
			GIVEAWAY[giveaway_id]["user_out"].remove(payload.user_id)

		print(f"GIVEAWAY: added {payload.user_id} to {giveaway_id}")
		await send_message(
			get_user(payload.user_id),
			f"**Successfully** joined the giveaway id __{giveaway_id}__"
		)
