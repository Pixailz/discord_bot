#!/usr/bin/env python

import os
from bot import DBWrapper
from bot import pprint

if __name__ == "__main__":
	test = DBWrapper("db.sqlite3")

	# test.create_user(10)
	# test.create_user(20)
	# test.create_user(30)

	# test.create_guild(100)
	# test.create_guild(200)
	# test.create_guild(300)

	# test.create_role(1000, 100)
	# test.create_role(2000, 100)
	# test.create_role(3000, 100)

	# test.create_user_in_guild(10, 100)
	# test.create_user_in_guild(20, 100)
	# test.create_user_in_guild(30, 100)
	# test.create_user_in_guild(10, 300)
	# test.create_user_in_guild(20, 300)
	# test.create_user_in_guild(30, 300)

	# test.create_channel(10000, "text", 1)
	# test.create_channel(20000, "voice", 1)
	# test.create_channel(30000, "text", 3)

	# test.create_message(100000, 2)
	# test.create_message(200000, 2)
	# test.create_message(300000, 3)
	# test.create_message(400000, 3)

	# test.create_giveaway("test_giveaway_01")
	# test.create_giveaway("test_giveaway_02")

	# def test_get(title, table):
	# 	print(title)
	# 	pprint(test.get(table, "*"))
	# 	print()

	# # pprint(test.get("sqlite_master", "*", [("type", "'table'")]))

	# test_get("User", "user")
	# test_get("Guild", "guild")
	# test_get("Role", "role")
	# test_get("User in Guild", "user_guild")
	# test_get("Channel", "channel")
	# test_get("Message", "message")
	# test_get("Giveaway", "giveaway")

	# TEST RELATION
	pprint(test.get_one(
		"giveaway ga",
		"ga.key, ga.name, m.id",
		join=[("message m", "ga.message_key", "m.key")],
		where=[("m.id", 1242111523627733053)],
		# "ga.key, ga.name, m.id, c.id, gu.id",
		# join=[
		# 	("message m", "ga.message_key", "m.key"),
		# 	("channel c", "m.channel_key", "c.key"),
		# 	("guild gu", "c.guild_key", "gu.key")
		# ]
	))
