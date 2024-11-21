from bal_common import *
from bal_chipmult import ChipMult
from bal_playingcard import PlayingCard
from bal_hand import Hand
from bal_deck import Deck
from bal_jokers import JokerCard, JOKERS
from typing import Any

with open(f"{DIR}/bal_log.txt", "w", encoding="utf-8") as f:
    f.write("")


def logprint(*args):
    string = " ".join([str(a) for a in args])
    print(string)
    with open(f"{DIR}/bal_log.txt", "a", encoding="utf-8") as f:
        f.write(string + "\n")


class Session:

    def __init__(self, input_file: str) -> None:
        inputs = input_file.split("\n")

        self.handsize = 6
        self.start_hands = 4
        self.now_hands = 4
        self.start_discards = 4
        self.now_discards = 4

        self.money = 0
        self.straightflushsize = 5

        self.cavendishspawn = False
        self.brokenglasscards = 0

        self.jokers: list[JokerCard] = []
        self.consumables: list[Any] = []
        self.chipmult = ChipMult((0, 0))

        fields = {
            "jokers": "",
            "hand": "",
            "selected": "",
            "levels": "",
            "deck": "",
            "discards": ""
        }
        for field in inputs:
            splitpoint = field.find(":")
            name, data = field[:splitpoint], field[splitpoint + 1:].lstrip()
            fields[name] = data

        self.selected = [
            int(i) - 1 for i in fields["selected"].split(" ") if i
        ]
        self.heldhand = Hand(self,
                             self.playing_cards_from_string(fields["hand"]))
        self.deck = Deck(self, self.playing_cards_from_string(fields["deck"]))
        self.jokers_from_string(fields["jokers"])
        self.levels_from_string(fields["levels"])
        if (d := fields["discards"]): self.discards = int(d)

    def replenishhand(self) -> None:
        while self.deck.cards and len(self.heldhand.cards) < self.handsize:
            i = randint(0, len(self.deck) - 1)
            self.heldhand.append(self.deck.cards.pop(i))
        self.heldhand.sort()

    def card_from_string(self, cardstr: str):
        chars = [*cardstr.upper()]

        suit = ALPHA_SUIT[chars.pop(0)]

        value = chars.pop(0)

        if value == "1" and chars[0] == "0":
            value += chars.pop(0)
        elif value == "1":
            value = "A"
        elif value == "11":
            value = "A"

        optional = [c if c != "-" else None for c in chars]
        optional += [None] * (3 - len(optional))

        playingcard = PlayingCard(self, suit, value, *optional)

        return playingcard

    def playing_cards_from_string(self, user_input: str) -> None:
        cards = []
        for cardinput in user_input.split(" "):
            cardinput = cardinput.split("*")
            cardstr = cardinput.pop(0)
            if not cardstr: continue
            count = int(cardinput[0]) if cardinput else 1
            for _ in range(count):
                card = self.card_from_string(cardstr)
                cards.append(card)
        return cards

    def joker_from_string(self, jokerstr: str):

        name, *attr = jokerstr.split(":")

        if name[-1].isupper():
            name, edition = name[:-1], name[-1]
        else:
            edition = None

        bestmatches = {
            "".join([c.lower() for c in name if c.isalnum()]): name
            for name in JOKERS.keys()
        }

        bestmatch = bestmatches[name]
        jokerclass = JOKERS[bestmatch]
        jokercard = jokerclass(self, edition, attr)

        return jokercard

    def jokers_from_string(self, user_input: str) -> None:
        for cardstr in user_input.split(" "):
            if not cardstr: continue
            card = self.joker_from_string(cardstr)
            self.jokers.append(card)

    def levels_from_string(self, user_input: str) -> None:
        self.handlevels = {name: 1 for name in POKER_HANDS.keys()}
        for handstr in user_input.lower().split(" "):
            namestr, lvl = handstr.split(":")
            best_fit_names = [
                name for name in self.handlevels.keys()
                if name.replace(" ", "") == namestr
            ]
            if not best_fit_names:
                logprint(
                    f'{colorcode(COMMON_COLORS["mult"])}unrecognized poker hand: "{namestr}"{COLORSTOP}'
                )
                continue
            self.handlevels[best_fit_names[0]] = int(lvl)

    def getscore(self) -> None:
        selected = self.selected
        if len(selected) != len(set(selected)):
            raise IndexError("card attempted to be played multiple times")

            #default before checking for gamerule changing cards
        self.CHANCEOF = 1
        self.CONSIDERED_FACE = set(FACE_VALS)
        self.CONSIDERED_SPADE = {ALPHA_SUIT["S"]}
        self.CONSIDERED_HEART = {ALPHA_SUIT["H"]}
        self.CONSIDERED_CLUB = {ALPHA_SUIT["C"]}
        self.CONSIDERED_DIAMOND = {ALPHA_SUIT["D"]}
        for i, joker in enumerate(self.jokers):
            joker.eval_rulechange()

        self.totalhand = Hand(self, self.heldhand.cards.copy())

        self.playedhand = Hand(self)
        for i in selected:
            self.playedhand.append(self.heldhand.cards[i])

        self.heldhand.remove(self.playedhand.cards)

        self.allhandtypes = self.playedhand.handtype()

        self.handtype, self.scoredcards = list(self.allhandtypes.items())[0]
        self.scoredcards = Hand(self, self.scoredcards)

        otherhands = []

        for handtype, scoredcards in list(self.allhandtypes.items())[1:]:
            scoredcards = Hand(self, scoredcards)
            otherhands.append(f"{handtype}:".ljust(20) + f"[{scoredcards}]")
        otherhands = "{" + ", \n".join(otherhands) + "}"

        handlevel = self.handlevels[self.handtype]
        self.chipmult = ChipMult(POKER_HANDS[self.handtype])
        logprint("DEBUG!", self.chipmult)
        self.chipmult.pluschip(PLANET_CARDS[self.handtype][0] *
                               (handlevel - 1))
        self.chipmult.plusmult(PLANET_CARDS[self.handtype][1] *
                               (handlevel - 1))
        logprint("DEBUG!", self.chipmult, self.chipmult.chip)

        logprint("deck:".ljust(20), self.deck)
        logprint("jokers:".ljust(53) + ", ".join([str(c)
                                                  for c in self.jokers]))
        logprint("total hand:".ljust(20), self.totalhand)
        logprint("played hand:".ljust(20), self.playedhand)
        logprint("held hand:".ljust(20), self.heldhand)
        logprint("hand type:".ljust(20), self.handtype)
        #logprint("other hands:".ljust(20), otherhands, sep="\n")
        logprint("scored cards:".ljust(20), self.scoredcards)

        logprint(
            f"base score of {self.handtype} (lvl {handlevel}):".ljust(53) +
            str(self.chipmult))

        for i, card in enumerate(self.heldhand.cards):
            if card.seal == "R": self.heldhand.retriggers[i] += 1

        for i, card in enumerate(self.scoredcards.cards):
            if card.seal == "R": self.scoredcards.retriggers[i] += 1

        for i, joker in enumerate(self.jokers):
            joker.eval_beforehand()

        #played cards
        zipped = zip(self.scoredcards.cards, self.scoredcards.retriggers)
        for i, (card, retriggers) in enumerate(zipped):

            for j in range(retriggers + 1):
                pre = str(self.chipmult)
                th = ["th", "st", "nd", "rd", *("th", ) * 6][(j + 1) % 10]
                card.eval_played()
                string = f"played card #{i+1} ({j+1}{th}): {card}"
                ljust_by = max(0, 53 - len(draincolor(string)))
                string += f"{' '*ljust_by}{pre}\t-->\t{self.chipmult}"
                logprint(string)

                for k, joker in enumerate(self.jokers):
                    joker.eval_played_card(card)

        #held in hand
        zipped = zip(self.heldhand.cards, self.heldhand.retriggers)
        for i, (card, retriggers) in enumerate(zipped):

            for j in range(retriggers + 1):
                pre = str(self.chipmult)
                #raise NotImplementedError("wa")
                card.eval_held()
                if pre != str(self.chipmult):
                    th = ["th", "st", "nd", "rd", *("th", ) * 6][(j + 1) % 10]
                    string = f"held card #{i+1} ({j+1}{th}): {card}"
                    ljust_by = max(0, 53 - len(draincolor(string)))
                    string += f"{' '*ljust_by}{pre}\t-->\t{self.chipmult}"
                    logprint(string)

                for k, joker in enumerate(self.jokers):
                    joker.eval_held_card(card)

        for i, joker in enumerate(self.jokers):
            joker.eval_afterhand()
            joker.eval_edition()

        i = 0
        while i < len(self.jokers):
            joker = self.jokers[i]
            if joker.broken and joker.name == "Gros Michel":
                self.cavendishspawn = True
                del self.jokers[i]  #<- untested
            else:
                i += 1

        i = 0
        while i < len(self.jokers):
            joker = self.jokers[i]
            if joker.broken:
                if joker.enhancement == "G":
                    self.brokenglasscards += 1
            else:
                i += 1

        logprint("remaining scored cards:".ljust(20), self.scoredcards)
        logprint("remaining jokers:".ljust(53) +
                 ", ".join([str(c) for c in self.jokers]))
