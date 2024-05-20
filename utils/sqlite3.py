from bot import sqlite3
from bot import datetime

from bot import DB_FILE

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


class DBWrapper:
	def __init__(self, db_name):
		self.db = sqlite3.connect(db_name)
		self.cur = self.db.cursor()

		self.init_db()
		self.db.commit()

	def __del__(self):
		self.db.close()

	def create_table(self, name, col):
		# print(f"CREATE TABLE IF NOT EXISTS {name} ({col}\n);")
		self.cur.execute(f"CREATE TABLE IF NOT EXISTS {name} ({col}\n);")

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


	# FUNCTION
	## GET
	def get(self,
			table: str,
			select: str = "*",
			where: list[tuple] = None,
			col: str = None,
			order: str = "ASC",
			join: list[tuple] = None,
		):

		req = f"SELECT {select} FROM {table}"

		if join is not None:
			for k, v in enumerate(join):
				req += f" JOIN {v[0]} ON {v[1]} = {v[2]}"

		if where is not None:
			for k, v in enumerate(where):
				if not k:
					req += " WHERE "
				else:
					req += " AND "

				req += f"{v[0]} = {v[1]}"

		if col is not None:
			req += f" ORDER BY {col} {order}"

		req += ";"
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

	## CREATE
	def create_user(self, user_id):
		self.cur.execute(f"""
			INSERT INTO {NameTable.user} (id)
			VALUES ({user_id});
		""")
		self.db.commit()
		return True, self.cur.lastrowid

	def create_guild(self, guild_id):
		self.cur.execute(f"""
			INSERT INTO {NameTable.guild} (id)
			VALUES ({guild_id});
		""")
		self.db.commit()
		return True, self.cur.lastrowid

	def create_role(self, role_id, guild_id):
		guild_key = self.get_one(NameTable.guild, "key", [("id", guild_id)])
		if guild_key is None:
			return False, -1
		guild_key = guild_key[0]

		self.cur.execute(f"""
			INSERT INTO {NameTable.role} (id, guild_key)
			VALUES ({role_id}, {guild_key});
		""")
		self.db.commit()
		return True, self.cur.lastrowid

	def create_user_in_guild(self, user_id, guild_id):
		user_key = self.get_one(NameTable.user, "key", [("id", user_id)])
		if user_key is None:
			return False, -1
		user_key = user_key[0]
		guild_key = self.get_one(NameTable.guild, "key", [("id", guild_id)])
		if guild_key is None:
			return False, -1
		guild_key = guild_key[0]

		self.cur.execute(f"""
			INSERT INTO {NameTable.user_guild} (user_key, guild_key)
			VALUES ({user_key}, {guild_key});
		""")
		self.db.commit()
		return True, self.cur.lastrowid

	def create_channel(self, channel_id, channel_type, guild_key):
		guild_key = self.get_one(NameTable.guild, "key", [("key", guild_key)])
		if guild_key is None:
			return False, -1
		guild_key = guild_key[0]

		self.cur.execute(f"""
			INSERT INTO {NameTable.channel} (id, type, guild_key)
			VALUES ({channel_id}, \"{channel_type}\", {guild_key});
		""")
		self.db.commit()
		return True, self.cur.lastrowid

	def create_message(self, message_id, channel_key):
		channel_key = self.get_one(NameTable.channel, "key", [("key", channel_key)])
		if channel_key is None:
			return False, -1
		channel_key = channel_key[0]

		self.cur.execute(f"""
			INSERT INTO {NameTable.message} (id, channel_key)
			VALUES ({message_id}, {channel_key});
		""")
		self.db.commit()
		return True, self.cur.lastrowid

	def create_giveaway(self, name):
		self.cur.execute(f"""
			INSERT INTO {NameTable.giveaway} (name, created)
			VALUES ("{name}", {datetime.datetime.now().timestamp()});
		""")
		self.db.commit()
		return True, self.cur.lastrowid

	## CREATE AND GET
	def cget_guild(self, guild_id):
		guild_key = self.get_one(NameTable.guild, "key", [("id", guild_id)])
		if guild_key is None:
			return self.create_guild(guild_id)

		return True, guild_key[0]

	def cget_user(self, user_id):
		user_key = self.get_one(NameTable.user, user_id)
		if user_key is None:
			return self.create_user(user_id)
		return True, user_key[0]

	def cget_channel(self, channel_id, channel_type, guild_key):
		channel_key = self.get_one(NameTable.channel, "key", [("id", channel_id)])
		if channel_key is None:
			return self.create_channel(channel_id, channel_type, guild_key)
		return True, channel_key[0]

	def cget_message(self, message_id, channel_key):
		message_key = self.get_one(NameTable.message, "key", [("id", message_id)])
		if message_key is None:
			return self.create_message(message_id, channel_key)
		return True, message_key[0]

	def cget_user_in_guild(self, user_id, guild_id):
		retv, user_key = self.cget_user(user_id)
		if not retv:
			return False, -1

		retv, guild_key = self.cget_guild(guild_id)
		if not retv:
			return False, -1

		user_guild_key = self.get_one(NameTable.user_guild, "key", [
			("user_key", user_key),
			("guild_key", guild_key)
		])
		if user_guild_key is None:
			return self.create_user_in_guild(user_key, guild_key)
		return True, user_guild_key[0]

	def cget_role(self, role_id, guild_id):
		role_key = self.get_one(NameTable.role, "key", [("id", role_id)])
		if role_key is None:
			retv, guild_key = self.cget_guild(guild_id)
			if not retv:
				return False, -1
			return self.create_role(role_id, guild_key)
		return True, role_key[0]

	## GIVEAWAY
	def register_giveaway_message(self, giveaway_key, message):
		giveaway_key = self.get_one(NameTable.giveaway, "key", [("key", giveaway_key)])
		if giveaway_key is None:
			return False
		giveaway_key = giveaway_key[0]

		retv, guild_key = self.cget_guild(message.guild.id)
		if retv is False:
			return False

		retv, channel_key = self.cget_channel(
			message.channel.id,
			message.channel.type,
			guild_key
		)
		if retv is False:
			return False

		retv, message_key = self.cget_message(message.id, channel_key)
		if retv is False:
			return False

		self.cur.execute(f"""
			UPDATE {NameTable.giveaway}
			SET message_key = {message_key}
			WHERE key = {giveaway_key};
		""")
		self.db.commit()
		return True

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
