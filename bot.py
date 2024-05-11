import os
import re
import sys
import json
import copy
import time
import signal
import urllib
import typing
import asyncio
import discord
import datetime
import logging
import itertools
import logging.handlers
import yt_dlp

from urllib.request import Request
from urllib.parse import urlparse
from urllib.parse import parse_qs

from discord.ext import commands
from discord import app_commands
from asyncio import sleep
from yt_dlp import YoutubeDL
from typing import Union, Optional, Literal

from pprint import pprint

DIR_BASE		= os.path.dirname(os.path.realpath(__file__))

DIR_DATA		= os.path.join(DIR_BASE, "data")

GIVEAWAY_FILE	= os.path.join(DIR_DATA, "giveaway.json")
LOG_FILE		= os.path.join(DIR_DATA, "bot.log")
IDS_FILE		= os.path.join(DIR_DATA, "ids.json")

def signal_handler(sig, frame):
	retv = 0
	if sig == signal.SIGINT:
		print("\nCTRL+C")
		retv = 130
	print("Saving giveaway")
	with open(GIVEAWAY_FILE, "w") as f:
		json.dump(GIVEAWAY, f, indent=4)
	print("Saved giveaway")

	print("Saved state")

	sys.exit(retv)


def have_role(user, role_id: int):
	if not getattr(user, "roles", None):
		return False
	for role in user.roles:
		if role.id == role_id:
			return True
	return False

def have_roles(user, role_id: [int]):
	for role in role_id:
		if have_role(user, role):
			return True
	return False

if not os.path.isdir(DIR_DATA):
	os.mkdir(DIR_DATA)

if os.path.exists(GIVEAWAY_FILE):
	with open(GIVEAWAY_FILE, "r") as f:
		GIVEAWAY = json.load(f)
else:
	GIVEAWAY = dict()

if os.path.exists(IDS_FILE):
	with open(IDS_FILE, "r") as f:
		IDS = json.load(f)
else:
	IDS = dict()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGUSR2, signal_handler)

with open(".env", "r") as f:
	ENV = json.load(f)

ALLOWED_BRO = [
	IDS["USER"]["pix"],
	IDS["USER"]["poney"],
	IDS["USER"]["kelly"],
	IDS["USER"]["arty"],
]

BAD_WORD = [
	"bastard",
	"cock",
	"cunt",
	"fuck",
	"onlyfan",
	"nigga",
	"nigge",
	"nudes",
	"porn",
	"pussy",
]

MODERATED_GUILD = {
	IDS["GUILD"]["SBA"]: {
		"url": None,
		"words": [
			*BAD_WORD,
			"pendisupendi",
			"ajrankamil",
		]
	},
	IDS["GUILD"]["server_test"]: {
		"url": None,
		"words": [
			*BAD_WORD,
		]
	}
}

LAST_RECEIVED = None

logger = logging.getLogger('discord')
handler = logging.handlers.RotatingFileHandler(
    filename=LOG_FILE,
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
	mode="w"
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler(sys.stdout))

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
	command_prefix='>>',
	intents=intents,
	permissions=discord.Permissions.administrator
)
bot.remove_command('help')

sys.set_int_max_str_digits(10000)

from utils.user import get_user
from utils.user import get_author
from utils.user import print_user

from utils.youtube import search_yt_video
from utils.youtube import search_yt_playlist
from utils.youtube import ytdl
from utils.youtube import FFMPEG_OPTIONS

from utils.send import send_message
from utils.send import send_embed

from utils.check import is_bro
from utils.check import extended_check
from utils.check import is_allowed

from utils.embed import get_embed

from utils.random import get_random_bytes

from utils.variate import word as variate_word

from utils.re import r

from utils.mee6 import get_mee6_leaderboard

from command.spam.cmd import spam_exec

# CMD
from command.spam.cmd import spam_cmd

# COG
from cog.Music		import MusicCOG
from cog.Random		import RandomCOG
from cog.Giveaway	import GiveawayCOG
from cog.Sync		import SyncCOG
from cog.Date		import DateCOG
from cog.Dump		import DumpCOG

# INTERACTION

## CMD
import command.spam.interaction.cmd

## MEMBER
import command.show.join_date.interaction.member
import command.show.pp.interaction.member

# EVENT
# import event.on_command_error
import event.on_message
import event.on_ready

from command.help.cmd import CustomHelp

asyncio.run(bot.add_cog(MusicCOG(bot)))
asyncio.run(bot.add_cog(RandomCOG(bot)))
asyncio.run(bot.add_cog(GiveawayCOG(bot)))
asyncio.run(bot.add_cog(SyncCOG(bot)))
asyncio.run(bot.add_cog(DateCOG(bot)))
asyncio.run(bot.add_cog(DumpCOG(bot)))

def bot_run():
	bot.help_command = CustomHelp()
	bot.run(
		ENV["DISCORD_TOKEN"],
		log_handler=handler
	)
