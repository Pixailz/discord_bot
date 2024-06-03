from bot import urllib
from bot import Request

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
		p.warn(f"Failed to decode {request.full_url}")
	return html

def req_open(request):
	try:
		resp = urllib.request.urlopen(request)
	except urllib.request.HTTPError as e:
		if e.code == 410 and request.host == "fossies.org":
			return req_decode(e)
		else:
			p.warn(f"Failed request, {e.code}, to {request.full_url}")
			return None

	return req_decode(resp)

def	get_mee6_leaderboard(guild_id):
	req = Request("https://mee6.xyz/api/plugins/levels/leaderboard/" + guild_id)
	req.add_header({"Authorization": ENV["MEE6_TOKEN"]})
	html = req_open(req)
	print(html)
	return html
