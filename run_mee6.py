import json
import urllib
from urllib.request import Request

with open(".env", "r") as f:
	ENV = json.load(f)

def req_decode(resp):
	if resp.info().get("Content-Encoding") == "gzip":
		raw = gzip.decompress(resp.read())
	else:
		raw = resp.read()
	resp.close()

	html = None
	try:
		html = raw.decode("utf-8")
	except UnicodeDecodeError:
		print(f"Failed to decode {request.full_url}")
	return html

def req_open(request):
	try:
		resp = urllib.request.urlopen(request)
	except urllib.request.HTTPError as e:
		if e.code == 410 and request.host == "fossies.org":
			return req_decode(e)
		else:
			print(f"Failed request, {e.code}, to {request.full_url}")
			return None

	return req_decode(resp)

def can_participate(user):
	if user["level"] >= 2:
		return True
	# if user["xp"] >= 1000:
	# 	return True
	return False

def	get_mee6_leaderboard(guild_id):
	req = Request(f"https://mee6.xyz/api/plugins/levels/leaderboard/{guild_id}")
	req.add_header("Authorization", ENV["MEE6_TOKEN"])
	req.add_header("user-agent", "")

	with open("mee6_leaderboard.json", "w") as f:
		json.dump(json.loads(req_open(req)), f, indent=4)
	with open("mee6_leaderboard.json", "r") as f:
		html_json = json.load(f)

	i = 0
	for user in html_json["players"]:
		i += 1
		print(f"{i:4d}", end="")
		if can_participate(user):
			print(f"{user['xp']:8d} (\x1b[32m{user['level']}\x1b[0m) {user['username']} ({user['id']})")
		else:
			print(f"{user['xp']:8d} (\x1b[31m{user['level']}\x1b[0m) {user['username']} ({user['id']})")

get_mee6_leaderboard(1066255709806792734)
