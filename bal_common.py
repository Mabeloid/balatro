from random import randint
import os

DIR = os.path.dirname(__file__)

def colorcode(color: int | str) -> str:
    return f"\u001b[38;5;{color}m"


COMMON_COLORS = {"chip": 33, "mult": 9, "luck": 10, "gold": 214}
BOLD = "\u001b[1m"
COLORSTOP = "\u001b[0m"


def draincolor(text: str) -> str:
    while (colorfrom := text.find("\u001b")) != -1:
        coloruntil = text.find("m", colorfrom)
        if coloruntil == -1: break
        text = text[:colorfrom] + text[coloruntil + 1:]
    return text


def color_cm(number: int | float, mode: int) -> str:
    if mode in (0, 1):
        sign = "+" if number >= 0 else ""
    else:
        sign = "X"
    if mode in (1, 2): color = COMMON_COLORS["mult"]
    else: color = COMMON_COLORS["chip"]
    color = colorcode(color)
    string = f"{sign}{color}{number}{COLORSTOP}"
    return string


SUITCOLOR = {"♦": 202, "♣": 8, "♥": 1, "♠": 16, "?": 243}
EDITION_COLOR = {
    "F": 69,
    "H": 219,
    "P": 51,
    "N": 235,
}
ENHANCEMENT_COLOR = {
    "B": COMMON_COLORS["chip"],
    "M": COMMON_COLORS["mult"],
    "W": 52,
    "G": 159,
    "S": 250,
    "R": 243,
    "O": COMMON_COLORS["gold"],
    "L": 229,
}
SEAL_COLOR = {"R": 9, "P": 39, "T": 135, "G": COMMON_COLORS["gold"]}

#

SUITS = ["♦", "♣", "♥", "♠"]
SUITS = {v: i for i, v in enumerate(SUITS)}
SUITS["?"] = -1
ALPHA_SUIT = {"D": "♦", "C": "♣", "H": "♥", "S": "♠", "?": "?"}

FACE_VALS = ["J", "Q", "K"]

VALUES = [str(i) for i in range(2, 11)] + FACE_VALS + ["A"]
VALUES = {v: i for i, v in enumerate(VALUES)}
VALUES["?"] = -1

#full names

ENHANCEMENT_FULL = {
    "B": "bonus",
    "M": "mult",
    "W": "wild",
    "G": "glass",
    "S": "steel",
    "R": "stone",
    "O": "gold card",
    "L": "lucky"
}

EDITION_FULL = {
    "F": "foil",
    "H": "holographic",
    "P": "polychrome",
    "N": "negative",
}

SEAL_FULL = {"R": "repeat seal", "P": "planet", "T": "tarot", "G": "gold seal"}

#scores

VALUESCORE = {str(i): i for i in range(2, 11)}
VALUESCORE.update({face: 10 for face in FACE_VALS})
VALUESCORE["A"] = 11
VALUESCORE["?"] = 0

POKER_HANDS = {
    "high card": (5, 1),
    "pair": (10, 2),
    "two pair": (20, 2),
    "three of a kind": (30, 3),
    "straight": (30, 4),
    "flush": (35, 4),
    "full house": (40, 4),
    "four of a kind": (60, 7),
    "straight flush": (100, 8)
}
POKER_HANDS.update({
    "five of a kind": (120, 12),
    "flush house": (140, 14),
    "flush five": (160, 16)
})

HANDS_SUBSET = {
    "flush five": ("five of a kind", "flush"),
    "flush house": ("full house", "flush"),
    "five of a kind": ("four of a kind", ),
    "four of a kind": ("three of a kind", ),
    "three of a kind": ("pair", ),
    "full house": ("three of a kind"),
}

PLANET_CARDS: dict[str, tuple[int, int]] = {
    "high card": (10, 1),
    "pair": (15, 1),
    "two pair": (20, 1),
    "three of a kind": (20, 2),
    "straight": (30, 2),
    "flush": (15, 2),
    "full house": (25, 2),
    "four of a kind": (30, 3),
    "straight flush": (40, 3)
}
PLANET_CARDS.update({
    "five of a kind": (35, 3),
    "flush house": (40, 3),
    "flush five": (40, 3)
})
