from bot import discord

from bot import bot, send_message, print_user, get_author, is_bro

@bot.event
async def on_command_error(ctx, error):
	author = get_author(ctx)
	print(f"An error occurred with user {print_user(author.id)}:\n> {error}")
	# if is_bro(author):
	# 	await send_message(ctx, f"An error occurred: {error}")
