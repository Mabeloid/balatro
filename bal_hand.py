from bal_common import *
from bal_playingcard import PlayingCard

class Session:
    straightflushsize: int

class Hand:

    def __init__(self, game: Session, in_cards: list[str] = []) -> None:
        self.game = game
        self.cards: list[PlayingCard] = []
        self.retriggers: list[int] = []
        for card in in_cards:
            self.append(card)
        self.sortmode = False

    def append(self, card: PlayingCard):
        self.cards.append(card)
        self.retriggers.append(0)

    def remove(self, input: PlayingCard | list[PlayingCard] | slice):
        if isinstance(input, PlayingCard):
            if not input in self.cards: return
            i = self.cards.index(input)
            del self.cards[i]
            del self.retriggers[i]
        elif isinstance(input, list):
            for card in input:
                self.remove(card)
        elif isinstance(input, slice):
            raise NotImplementedError("Hand.remove(slice)")
        else:
            raise NotImplementedError("Hand.remove(unknown type)")

    def __str__(self) -> str:
        return ", ".join([str(card) for card in self.cards])

    def comparetwocards(self, check_card: PlayingCard,
                        best_so_far: PlayingCard) -> tuple[int, int]:
        x = SUITS[check_card.suit]
        y = SUITS[best_so_far.suit]
        suit_comp = (x > y) - (x < y)
        x = VALUES[check_card.value]
        y = VALUES[best_so_far.value]
        value_comp = (x > y) - (x < y)
        return suit_comp, value_comp

    def sort(self) -> None:
        if not self.cards: return
        newcards: list[PlayingCard] = []
        while self.cards[1:]:
            best_i = 0
            for i, card in enumerate(self.cards):
                suit_comp, value_comp = self.comparetwocards(
                    card, self.cards[best_i])
                if self.sortmode:
                    comp_first, comp_after = suit_comp, value_comp
                else:
                    comp_first, comp_after = value_comp, suit_comp

                if comp_first == 1:
                    best_i = i
                elif comp_first == 0:
                    if comp_after == 1: best_i = i

            newcards.append(self.cards.pop(best_i))
        newcards.append(self.cards[0])
        self.cards = newcards

    def handtype(self) -> dict[str, list[PlayingCard]]:

        debug = False

        def getprintlist(cardsdict: dict[str, list[PlayingCard]]) -> str:
            printlist = []
            for S, cards in cardsdict.items():
                printlist.append(
                    str(S) + ": [" + ", ".join([str(c) for c in cards]) + "]")
            print_str = "{" + ", ".join(printlist) + "}"
            return print_str

        STONE_CARDS = []
        i = 0
        while i < len(self.cards):
            card = self.cards[i]
            if card.enhancement == "R":
                STONE_CARDS.append(card)
                self.cards.remove(card)
            else:
                i += 1

        suits = {}
        for card in self.cards:
            S = None if card.enhancement == "W" else card.suit
            suits[S] = suits.get(S, 0) + 1

        suits_ = {}
        for card in self.cards:
            S = None if card.enhancement == "W" else card.suit
            suits_[S] = suits_.get(S, []) + [card]
        if debug: print("suits_:".ljust(15), getprintlist(suits_))

        s_count = {}
        for count in suits.values():
            s_count[count] = s_count.get(count, 0) + 1

        s_count_: dict[int, dict[str, list[PlayingCard]]] = {}
        for v, cards in suits_.items():
            if not len(cards) in s_count_.keys():
                s_count_[len(cards)] = {v: cards}
            else:
                s_count_[len(cards)].update({v: cards})
        printprintstrstr = "{" + ", ".join(
            [f"{k}: {getprintlist(v)}" for (k, v) in s_count_.items()]) + "}"
        if debug: print("s_count_:".ljust(15), printprintstrstr)

        values = {}
        for card in self.cards:
            values[card.value] = values.get(card.value, 0) + 1

        values_: dict[str, list[PlayingCard]] = {}
        for card in self.cards:
            values_[card.value] = values_.get(card.value, []) + [card]
        if debug: print("values_:".ljust(15), getprintlist(values_))

        v_count = {}
        for count in values.values():
            v_count[count] = v_count.get(count, 0) + 1

        v_count_: dict[int, dict[str, list[PlayingCard]]] = {}
        for v, cards in values_.items():
            if not len(cards) in v_count_.keys():
                v_count_[len(cards)] = {v: cards}
            else:
                v_count_[len(cards)].update({v: cards})
        printprintstrstr = "{" + ", ".join(
            [f"{k}: {getprintlist(v)}" for (k, v) in v_count_.items()]) + "}"

        if debug: print("v_count_:".ljust(15), printprintstrstr)

        SF_size = self.game.straightflushsize

        ways_to_royalstraight = [
            set(range(start, start + SF_size))
            for start in [range(8, 9), range(8, 10)][SF_size == 4]
        ]
        ways_to_straight = [
            set(range(start, start + 5)) for start in range(-1, (13 - 5) + 1)
        ]
        if SF_size == 4:
            ways_to_straight += [
                set(range(start, start + 4))
                for start in range(-1, (13 - 4) + 1)
            ]

        for straightway in ways_to_straight:
            if -1 in straightway:
                straightway.remove(-1)
                straightway.add(VALUES["A"])

        best_straight = {}
        for straightway in ways_to_straight:
            potential_straight = {
                VALUES[card.value]: card
                for card in self.cards if VALUES[card.value] in straightway
            }

            if len(potential_straight) < SF_size: continue
            if len(potential_straight) > len(best_straight):
                best_straight = potential_straight
            elif len(potential_straight) == len(best_straight):
                if max(potential_straight) > max(best_straight):
                    best_straight = potential_straight

        #-------------------

        five_dict = v_count_.get(5, {"": list()})
        five_list = list(five_dict.items())[0][1]

        four_dict = v_count_.get(4, {"": list()})
        four_list = list(four_dict.items())[0][1]
        four_list = four_list or five_list[:4]

        three_dict = v_count_.get(3, {"": list()})
        three_list = list(three_dict.items())[0][1]
        three_list = three_list or four_list[:3]

        pairs_dict = v_count_.get(2, {"": list()})
        onepair_list = list(pairs_dict.items())[0][1]
        onepair_list = onepair_list or three_list[:2]

        twopair_list = []
        if len(pairs_dict) > 1:
            twopair_list = onepair_list + list(pairs_dict.items())[1][1]

        card_vals = {card: VALUESCORE[card.value] for card in self.cards}
        highcard_list = [max(card_vals, key=card_vals.get)]

        house_list = list(set(three_list + onepair_list))
        if len(house_list) != 5: house_list = []

        flush_dict = s_count_[max(s_count_.keys())]
        flush_list = list(flush_dict.items())[0][1]
        if len(flush_list) < SF_size: flush_list = []

        if best_straight:
            straight_list = list(best_straight.values())
        else:
            straight_list = []

        if straight_list and flush_list:
            straightflush_list = [
                card for card in self.cards
                if card in straight_list + flush_list
            ]
        else:
            straightflush_list = []

        handtypes = {}

        if five_list and flush_list:
            handtypes["flush five"] = five_list + STONE_CARDS

        if house_list and flush_list:
            handtypes["flush house"] = house_list + STONE_CARDS

        if five_list:
            handtypes["five of a kind"] = five_list + STONE_CARDS

        if straightflush_list:
            handtypes["straight flush"] = straightflush_list + STONE_CARDS

        if four_list:
            handtypes["four of a kind"] = four_list + STONE_CARDS

        if house_list:
            handtypes["full house"] = house_list + STONE_CARDS

        if flush_list:
            handtypes["flush"] = flush_list + STONE_CARDS

        if straight_list:
            handtypes["straight"] = straight_list + STONE_CARDS

        if three_list:
            handtypes["three of a kind"] = three_list + STONE_CARDS

        if twopair_list:
            handtypes["two pair"] = twopair_list + STONE_CARDS

        if onepair_list:
            handtypes["pair"] = onepair_list + STONE_CARDS

        if highcard_list:
            handtypes["high card"] = highcard_list + STONE_CARDS

        for card in STONE_CARDS:
            self.append(card)
        return handtypes

    def __len__(self):
        return len(self.cards)