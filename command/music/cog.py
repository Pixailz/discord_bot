from bot import discord
from bot import datetime
from discord.ext import commands
from bot import Literal
from bot import urlparse
from bot import parse_qs
from bot import asyncio

from bot import pprint

from bot import is_allowed
from bot import send_message
from bot import send_embed
from bot import get_author
from bot import get_embed
from bot import search_yt_video
from bot import search_yt_playlist
from bot import ytdl
from bot import FFMPEG_OPTIONS

class MusicCOG(
		commands.Cog,
		name="Music",
	):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.is_playing = False
		self.queue = list()
		self.current_guild = None
		self.current_channel = None
		self.vc = None
		self.last_ctx = None

	g_main = discord.app_commands.Group(
		name="px_yt",
		description="Play Music in voice channel",
	)

	@commands.Cog.listener()
	async def on_ready(self):
		print("Music cog loaded")

	@staticmethod
	def add_vid_embed(vid, embed, index):
		embed.add_field(
			name=f"{index}. {vid['title']} "
				f"({str(datetime.timedelta(seconds=vid['duration']))})",
			value=f"From `{vid['channel']}`",
		)
		embed.set_image(url=vid['thumbnail'])

	async def yt_add_single(self, ctx, query):
		video_id = query.get("v", None)
		if video_id == None:
			await send_message(ctx, "Invalid Youtube URL")
			return

		await ctx.response.defer()

		vid = search_yt_video(video_id[0])
		vid["ctx"] = ctx
		self.last_ctx = vid["ctx"]
		self.queue.append(vid)

		embed = get_embed(ctx, f"Added {video_id} (single)")
		MusicCOG.add_vid_embed(vid, embed, len(self.queue))
		await send_embed(ctx, embed)

	async def yt_add_playlist(self, ctx, query):
		playlist_id = query.get("list", None)
		if playlist_id == None:
			await send_message(ctx, "Invalid Youtube Playlist URL")
			return

		await ctx.response.defer()

		vids = search_yt_playlist(playlist_id[0])

		for vid in vids:
			vid["ctx"] = ctx
			self.last_ctx = vid["ctx"]
			self.queue.append(vid)

			embed = get_embed(ctx, f"Added {vid['title']} (playlist)")
			MusicCOG.add_vid_embed(vid, embed, len(self.queue))
			await send_embed(ctx, embed)

	@g_main.command(name="add", description="Add music to the queue")
	@is_allowed()
	async def yt_add(self, ctx,
		target_url: str,
		target: Literal["single", "playlist"] = "single",
	):
		url = urlparse(target_url)
		if url == None:
			await send_message(ctx, "Invalid URL")
			return

		query = parse_qs(url.query)
		if query == None:
			await send_message(ctx, "Invalid URL")
			return

		if target == "single":
			await self.yt_add_single(ctx, query)
		else:
			await self.yt_add_playlist(ctx, query)

	@g_main.command(
		name="join",
		description="Make the bot join a voice channel",
	)
	@is_allowed()
	async def yt_join(self, ctx):
		author = get_author(ctx)
		try:
			self.current_channel = author.voice.channel
		except:
			await send_message(ctx,
				f"{author.mention} You need to be in a voice channel to use this command")
			return
		try:
			self.vc = await self.current_channel.connect()
		except discord.errors.ClientException as e:
			await send_message(ctx,
				f"{author.mention} I'm already in a voice channel")
			return

		if self.vc == None:
			await send_message(ctx,
				f"{author.mention} I cannot join this voice channel")
			return

		self.current_guild = ctx.guild
		await self.update_vc_state()
		await send_message(ctx, f"Successfully joined {self.current_channel}")

	@g_main.command(
		name="pause",
		description="Make the bot pause the music",
	)
	@is_allowed()
	async def yt_pause(self, ctx):
		self.is_playing = False
		await self.update_vc_state()
		await send_message(ctx, f"Successfully paused music {self.current_channel}")

	@g_main.command(
		name="resume",
		description="Make the bot resume the music",
	)
	@is_allowed()
	async def yt_resume(self, ctx):
		self.is_playing = True
		await self.update_vc_state()
		await send_message(ctx, f"Successfully resumed music {self.current_channel}")

	@g_main.command(
		name="leave",
		description="Make the bot leave from from voice channel",
	)
	@is_allowed()
	async def yt_leave(self, ctx):
		if self.vc and self.vc.is_connected():
			self.is_playing = False
			await self.update_vc_state()
			await self.vc.disconnect()
			await send_message(ctx, f"Successfully leaved {self.current_channel}")
		else:
			await send_message(ctx, f"Not in a channel")

	@g_main.command(
		name="skip",
		description="Skip current music in the queue",
	)
	@is_allowed()
	async def yt_skip(self, ctx):
		if len(self.queue) == 0:
			await send_message(ctx, "No music in the queue")
			return

		if self.vc and self.vc.is_playing():
			self.vc.stop()
			await send_message(ctx, f"Successfully skiped music {self.current_channel}")

	@g_main.command(
		name="play",
		description="Make the bot play the music",
	)
	@is_allowed()
	async def yt_play(self, ctx):
		if len(self.queue) == 0:
			self.is_playing = False
			await self.update_vc_state()
			await send_message(ctx, "No music in the queue")
			return
		if self.vc == None or not self.vc.is_connected():
			self.is_playing = False
			await self.update_vc_state()
			await send_message(ctx, "I am not connected to a voice channel")
			return

		self.is_playing = True
		await self.update_vc_state()

		embed = get_embed(ctx, f"Currently playing")
		MusicCOG.add_vid_embed(self.queue[0], embed, 1)
		await send_embed(ctx, embed)

		if self.vc and self.vc.is_playing():
			await send_message(ctx, "I'm **already** playing :)")
			return

		self.vc.play(
			discord.FFmpegPCMAudio(
				self.queue[0]["url"],
				executable= "ffmpeg",
				**FFMPEG_OPTIONS
			),
			after=lambda e: asyncio.run_coroutine_threadsafe(
				self.play_next(),
				self.bot.loop
			)
		)

	async def play_next(self, skip = False):
		self.queue.pop(0)
		if len(self.queue) == 0:
			self.is_playing = False
			await self.update_vc_state()
			await send_message(self.last_ctx, "No more music in the queue")
			return

		embed = get_embed(self.queue[0]["ctx"], f"Currently playing")
		MusicCOG.add_vid_embed(self.queue[0], embed, 1)
		await send_embed(self.queue[0]["ctx"], embed)

		self.vc.play(
			discord.FFmpegPCMAudio(
				self.queue[0]["url"],
				executable= "ffmpeg",
				**FFMPEG_OPTIONS
			),
			after=lambda e: asyncio.run_coroutine_threadsafe(
				self.play_next(),
				self.bot.loop
			)
		)

	@g_main.command(
		name="list",
		description="List current queue",
	)
	@is_allowed()
	async def yt_list(self, ctx):
		if len(self.queue) == 0:
			await send_message(ctx, "No music in the queue")
			return
		s = f"Current Queue ({len(self.queue)}):\n"
		for k, v in enumerate(self.queue):
			s += f"{k}. {v['title']} - {v['channel']} " + \
				f"({str(datetime.timedelta(seconds=v['duration']))})\n"
		await send_message(ctx, s)

	@g_main.command(
		name="clear",
		description="Clear current queue",
	)
	@is_allowed()
	async def yt_clear(self, ctx):
		self.queue = list()
		await self.update_vc_state()
		await send_message(ctx, f"Successfully cleared the queue")

	@staticmethod
	def get_vid_info(vid):
		return (
			"```"
			f"Title:     {vid['title']}\n"
			f"Url:       {vid['url']}\n"
			f"Duration:  {str(datetime.timedelta(seconds=vid['duration']))}\n"
			f"Thumbnail: {vid['thumbnail']}\n"
			f"Channel:   {vid['channel']}\n"
			"```"
		)

	async def update_vc_state(self):
		if self.current_channel is None or self.current_guild is None:
			return

		if len(self.queue) == 0:
			self.is_playing = False
		self_deaf = True
		self_mute = True
		if self.is_playing:
			self_deaf = False
			self_mute = False
			self.vc.resume()
		else:
			self.vc.pause()

		await self.current_guild.change_voice_state(
			channel=self.current_channel,
			self_deaf=self_deaf,
			self_mute=self_mute
		)
