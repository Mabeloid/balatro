from bal_common import *
from bal_playingcard import PlayingCard

class Session:
    ... #not actually used

class Deck:

    def __init__(self, game: "Session", cards: list[PlayingCard] = []) -> None:
        self.game = game
        self.cards = []
        for card in cards:
            self.append(card)

    def append(self, card: PlayingCard):
        self.cards.append(card)

    def default(self):
        self.cards = []
        for suit in SUITS:
            if suit == "?": continue
            for value in VALUES:
                if value == "?": continue
                self.append(PlayingCard(self.game, suit, value))

    def __str__(self) -> str:
        str_list = [str(card) for card in self.cards]
        card_dict = {card: str_list.count(card) for card in set(str_list)}
        return ", ".join(
            [f"{k}*{v}" if v != 1 else k for k, v in card_dict.items()])

    def __len__(self) -> int:
        return len(self.cards)