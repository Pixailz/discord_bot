from bot import YoutubeDL

YDL_OPTIONS = {
	"format": "bestaudio/best",
}

FFMPEG_OPTIONS = {
	"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
	"options": "-vn",
}

ytdl = YoutubeDL(YDL_OPTIONS)

def get_yt_info(info):
	return {
		"url": info["url"],
		"title": info["title"],
		"duration": info["duration"],
		"thumbnail": info["thumbnail"],
		"channel": info["channel"]
	}

def search_yt_video(video_id):
	url = f"https://youtu.be/watch?v={video_id}"
	info = ytdl.extract_info(url, download=False)
	return get_yt_info(info)

def search_yt_playlist(playlist_id):
	url = f"https://youtu.be/playlist?list={playlist_id}"
	info = ytdl.extract_info(url, download=False)

	retv = list()
	for entry in info["entries"]:
		retv.append(get_yt_info(entry))
	return retv
