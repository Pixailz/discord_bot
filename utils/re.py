from bot import re

class Regex():
	def __init__(self):
		self.link = re.compile(r"https?://.*")

r = Regex()
