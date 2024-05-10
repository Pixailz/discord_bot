from bot import send_message

def get_random_bytes(length: int = 4, mod: int = 0) -> int:
	with open("/dev/urandom", "rb") as f:
		random = f.read(length)
	res = int.from_bytes(random, byteorder="big")
	if mod != 0:
		res = (res % mod) + 1
	return res
