from bot import discord
from bot import sqlite3
from bot import datetime
from bot import ChannelABC
from bot import Literal

from bot import DB_FILE

DEBUG = True

channel_type = [
	"text",
	"voice",
	"private",
	"group",
	"category",
	"news",
	"stage_voice",
	"news_thread",
	"public_thread",
	"private_thread",
	"forum",
]

class NameTable:
	user = "user"
	guild = "guild"
	channel = "channel"
	message = "message"
	user_guild = "user_guild"
	role = "role"
	giveaway = "giveaway"
	user_giveaway = "user_giveaway"

class DBWrapper:
	def __init__(self, db_name: str):
		self.db = sqlite3.connect(db_name)
		self.cur = self.db.cursor()

		self.init_db()
		self.db.commit()

	def __del__(self):
		self.db.close()

	def create_table(self, name: str, col: str):
		req = f"CREATE TABLE IF NOT EXISTS {name} ({col}\n);"
		if DEBUG:
			print(req)
		self.cur.execute(req)

	def init_db(self):
		# USER
		self.create_table(NameTable.user, """
		key INTEGER PRIMARY KEY,

		id INTEGER""")

		# GUILD
		self.create_table(NameTable.guild, """
		key INTEGER PRIMARY KEY,

		id INTEGER""")

		## CHANNEL
		self.create_table(NameTable.channel, f"""
		key INTEGER PRIMARY KEY,

		id INTEGER,
		type TEXT CHECK(type IN ("{'", "'.join(channel_type)}")),

		guild_key INTEGER,
		FOREIGN KEY (guild_key) REFERENCES guild(key)
		ON DELETE CASCADE""")

		# ROLE
		self.create_table(NameTable.role, """
		key INTEGER PRIMARY KEY,
		id INTEGER,
		guild_key INTEGER,

		FOREIGN KEY (guild_key) REFERENCES guild(key)
		ON DELETE CASCADE""")

		## USER IN GUILD
		self.create_table(NameTable.user_guild, """
		key INTEGER PRIMARY KEY,

		user_key INTEGER,
		guild_key INTEGER,

		FOREIGN KEY (user_key) REFERENCES user(key)
		ON DELETE CASCADE,
		FOREIGN KEY (guild_key) REFERENCES guild(key)
		ON DELETE CASCADE""")

		## MESSAGE
		self.create_table(NameTable.message, """
		key INTEGER PRIMARY KEY,

		id INTEGER,

		channel_key INTEGER,
		FOREIGN KEY (channel_key) REFERENCES channel(key)
		ON DELETE CASCADE""")

		## GIVEAWAY
		self.create_table(NameTable.giveaway, """
		key INTEGER PRIMARY KEY,

		name TEXT,
		created REAL,

		message_key INTEGER DEFAULT NULL,
		FOREIGN KEY (message_key) REFERENCES message(key)
		ON DELETE CASCADE""")

		## USER IN GIVEAWAY
		self.create_table(NameTable.user_giveaway, f"""
		key INTEGER PRIMARY KEY,
		user_key INTEGER,
		giveaway_key INTEGER,

		first_interaction REAL,
		participate BOOL DEFAULT {True},
		has_win int DEFAULT 0,

		FOREIGN KEY (user_key) REFERENCES user(key)
		ON DELETE CASCADE,
		FOREIGN KEY (giveaway_key) REFERENCES giveaway(key)
		ON DELETE CASCADE""")


	# FUNCTION
	## CREATE
	def insert(self, table: str, col: list[str], value: list[str]):
		# req = f"INSERT INTO {table} (\"{'", "'.join(col)}\")"
		req = f"INSERT INTO {table} ({', '.join(col)})"
		req += f""" VALUES ({', '.join(
			[ str(i) for i in value ]
		)})"""
		if DEBUG:
			print(req)
		self.cur.execute(req)
		self.db.commit()
		return True, self.cur.lastrowid

	def update(self,
			table: str,
			value: list[tuple],
			where: list[tuple] = None
		):
		req = f"UPDATE {table}"

		for v in value:
			req += f" SET {v[0]} = {v[1]}"

		if where is not None:
			for k, v in enumerate(where):
				if not k:
					req += " WHERE "
				else:
					req += " AND "

				req += f"{v[0]} = {v[1]}"
		req += ';'

		if DEBUG:
			print(req)
		self.cur.execute(req)
		self.db.commit()
		return True, self.cur.lastrowid

	## GET
	def get(self,
			table: str,
			select: str = "*",
			where: list[tuple] = None,
			col: str = None,
			order: Literal["ASC", "DESC"] = "ASC",
			join: list[tuple] = None,
		):

		req = f"SELECT {select} FROM {table}"

		if join is not None:
			for v in join:
				req += f" JOIN {v[0]} ON {v[1]} = {v[2]}"

		if where is not None:
			for k, v in enumerate(where):
				if not k:
					req += " WHERE "
				else:
					req += " AND "
				if len(v) == 3:
					if v[0] == "NE":
						req += f"{v[1]} != {v[2]}"
				else:
					req += f"{v[0]} = {v[1]}"

		if col is not None:
			req += f" ORDER BY {col} {order}"

		req += ";"
		if DEBUG:
			print(req)
		res = self.cur.execute(req).fetchall()

		if len(res) == 0:
			return None
		return res

	def get_one(self,
			table: str,
			select: str = "*",
			where: list[tuple] = None,
			col: str = None,
			order: str = "ASC",
			join: list[tuple] = None,
		):
		res = self.get(table, select, where, col, order, join)
		if res is None:
			return None
		return res[0]

	def get_key(self, table: str, id: int,
			where: list[tuple] = None,
			join: list[tuple] = None
		):
		w = [("id", id)]
		if where is not None:
			for ww in where:
				w.append(ww)

		key = self.get_one(table, "key", where = w, join = join)
		return key[0] if key is not None else None

	def get_user_key(self, user_id: int):
		return self.get_key(NameTable.user, user_id)

	def get_guild_key(self, guild_id: int):
		return self.get_key(NameTable.guild, guild_id)

	def get_channel_key(self, channel: ChannelABC):
		return self.get_key(NameTable.channel, channel.id, [
			("type", f"'{channel.type}'")
		])

	def get_message_key(self, message_id: int):
		return self.get_key(NameTable.message, message_id)

	def get_role_key(self, role_id: int):
		return self.get_key(NameTable.role, role_id)

	def get_giveaway_key(self, message_id: int):
		key = self.get_one(f"{NameTable.giveaway} ga", "ga.key",
			where=[("m.id", message_id)],
			join=[("message m", "ga.message_key", "m.key")]
		)
		return key[0] if key is not None else None

	def get_user_giveaway_key(self, user_id: int, giveaway_key: int):
		key = self.get_one(f"{NameTable.user_giveaway} ug", "ug.key",
			join = [
				("user u", "ug.user_key", "u.key"),
				("giveaway g", "ug.giveaway_key", "g.key"),
			],
			where = [
				("u.id", user_id),
				("g.key", giveaway_key)
			],
		)
		return key[0] if key is not None else None

	## CREATE/GET
	def cget_user(self, user_id: int):
		user_key = self.get_user_key(user_id)
		if user_key is not None:
			return True, user_key

		return self.insert(NameTable.user, ["id"], [user_id])

	def cget_guild(self, guild_id: int):
		guild_key = self.get_guild_key(guild_id)
		if guild_key is not None:
			return True, guild_key

		return self.insert(NameTable.guild, ["id"], [guild_id])

	def cget_channel(self, channel: discord.abc.GuildChannel,
			guild_id: int
		):
		channel_key = self.get_channel_key(channel)
		if channel_key is not None:
			return True, channel_key

		_, guild_key = self.cget_guild(guild_id)

		return self.insert(NameTable.channel,
			["id", "type", "guild_key"],
			[channel.id, f"'{channel.type}'", guild_key]
		)

	def cget_role(self, role_id: int, guild_id: int):
		role_key = self.get_role_key(role_id)
		if role_key is not None:
			return True, role_key

		_, guild_key = self.cget_guild(guild_id)
		return self.insert(NameTable.guild,
			["id", "guild_key"],
			[role_id, guild_key]
		)

	def cget_message(self, message_id: int, channel: ChannelABC,
			guild_id: int
		):
		message_key = self.get_message_key(message_id)
		if message_key is not None:
			return True, message_key

		_, channel_key = self.cget_channel(channel, guild_id)
		return self.insert(NameTable.message,
			["id", "channel_key"],
			[message_id, channel_key]
		)

	def cget_giveaway(self, name: str):
		return self.insert(NameTable.giveaway,
			["name", "created"],
			[f"\"{name}\"", datetime.datetime.now().timestamp()]
		)

	def cget_user_guild(self, user_id, guild_id):
		_, user_key = self.cget_user(user_id)
		_, guild_key = self.cget_guild(guild_id)
		return self.insert(NameTable.user_giveaway,
			["user_key", "guild_key"],
			[user_key, guild_key]
		)

	def cget_user_giveaway(self, user_id: int, message_id: int):
		giveaway_key = self.get_giveaway_key(message_id)
		if giveaway_key is None:
			return False, f"Message id ({message_id}) not a Giveaway message"

		user_giveaway_key = self.get_user_giveaway_key(user_id, giveaway_key)
		if user_giveaway_key is not None:
			return True, user_giveaway_key

		_, user_key = self.cget_user(user_id)
		return self.insert(NameTable.user_giveaway,
			["giveaway_key", "user_key", "first_interaction"],
			[giveaway_key, user_key, datetime.datetime.now().timestamp()]
		)

	## GIVEAWAY
	def register_giveaway_message(self, giveaway_key, message):
		giveaway_key = self.get_one(NameTable.giveaway, "key", [("key", giveaway_key)])
		if giveaway_key is None:
			return False
		giveaway_key = giveaway_key[0]

		retv, message_key = self.cget_message(
			message.id,
			message.channel,
			message.guild.id
		)
		if retv is False:
			return False

		return self.update(NameTable.giveaway,
			[("message_key", message_key)],
			[("key", giveaway_key)]
		)

if __name__ == "__main__":
	import os
	os.system("rm test.db")

	test = DBWrapper("test.db")

	test.create_user(10)
	test.create_user(20)
	test.create_user(30)

	test.create_guild(100)
	test.create_guild(200)
	test.create_guild(300)

	test.create_role(1000, 100)
	test.create_role(2000, 100)
	test.create_role(3000, 100)

	test.create_user_in_guild(10, 100)
	test.create_user_in_guild(20, 100)
	test.create_user_in_guild(30, 100)
	test.create_user_in_guild(10, 300)
	test.create_user_in_guild(20, 300)
	test.create_user_in_guild(30, 300)

	test.create_channel(10000, "TEXT", 100)
	test.create_channel(20000, "VOICE", 100)
	test.create_channel(30000, "TEXT", 300)

	test.create_message(100000, 20000)
	test.create_message(200000, 20000)
	test.create_message(300000, 30000)
	test.create_message(400000, 30000)

	test.create_giveaway("test_giveaway_01")
	test.create_giveaway("test_giveaway_02")

	def test_get(title, table):
		print(title)
		pprint(test.get(f"SELECT * FROM {table};"))
		print()

	# pprint(test.get("SELECT * FROM sqlite_master WHERE type='table';"))

	test_get("User", "user")
	test_get("Guild", "guild")
	test_get("Role", "role")
	test_get("User in Guild", "user_guild")
	test_get("Channel", "channel")
	test_get("Message", "message")
	test_get("Giveaway", "giveaway")
