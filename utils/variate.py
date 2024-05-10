from bot import itertools
from bot import copy

VARIATION_SOFT = {
	"a": ["4", "@"],
	"b": ["ß"],
	"e": ["3"],
	"i": ["1"],
	"j": ["ʝ"],
	"l": ["1"],
	"m": ["nn"],
	"o": ["0"],
	"s": ["5", "$"],
	"u": ["v"],
	"v": ["u"],
	"w": ["vv"],
}

VARIATION_HARD = {
	"a": ["4", "@"],
	"b": ["8", "ß"],
	"e": ["3", "€"],
	"i": ["1", "|"],
	"j": ["ʝ"],
	"l": ["1", "|"],
	"m": ["nn"],
	"o": ["0", "()", "[]"],
	"s": ["5", "$"],
	"t": ["7", "+"],
	"u": ["v"],
	"v": ["u"],
	"w": ["vv"],
	"x": ["+"],
	"z": ["2", "7"],
}

def extrapolate_variation():
	new_variation = copy.deepcopy(VARIATION)

	for k, v in new_variation.items():
		for l in v:
			VARIATION[l] = [k, *v]

	# for k, v in VARIATION.items():
	# 	tmp = set(v)
	# 	VARIATION[l] = list(tmp)

VARIATION = VARIATION_HARD
VARIATION_CACHE = dict()

extrapolate_variation()

def word(word):
	if word in VARIATION_CACHE:
		return VARIATION_CACHE[word]

	letters = list()
	words = list()
	word = word.lower()

	for l in word:
		if l in VARIATION:
			letters.append([l, *VARIATION[l]])
		else:
			letters.append([l])

	letters = list(itertools.product(*letters))

	for w in letters:
		words.append("".join(w))

	VARIATION_CACHE[word] = words
	return words
