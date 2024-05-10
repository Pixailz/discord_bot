from bot import discord
from bot import bot
from bot import IDS

def get_user(user: any):
	if user is None:
		print(f"Cannot convert {user} to discord.User")
		return None

	if isinstance(user, str):
		if user.startswith("<@"):
			return bot.get_user(int(user[2:-1]))
		elif IDS["USER"].get(user):
			return bot.get_user(IDS["USER"][user])
	elif isinstance(user, int):
		return bot.get_user(user)
	elif isinstance(user, discord.User):
		return user
	else:
		try:
			return bot.get_user(int(user))
		except ValueError:
			print(f"Cannot convert {user} to discord.User")
			return None

def get_author(context: any):
	author = None
	if isinstance(context, discord.Interaction):
		author = context.user
	elif isinstance(context, discord.ext.commands.Context):
		author = context.author
	return author

def print_user(user):
	if not user:
		return f"{user} (NOT FOUND)"
	user = get_user(user)
	if not user:
		return f"{user} (NOT FOUND)"
	return f"`{user.name}` ({user.id})"
