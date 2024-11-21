from bal_common import *
from bal_chipmult import ChipMult


class Hand:
    cards: list["PlayingCard"]
    retriggers: list[int]


class Deck:
    cards: list["PlayingCard"]


class Session:
    handsize: int
    handcount: int
    discards: int
    money: int
    straightflushsize: int

    cavendishspawn: bool
    brokenglasscards: int

    chipmult: ChipMult

    jokers: list["JokerCard"]
    deck: Deck
    playedhand: Hand
    heldhand: Hand
    totalhand: Hand

    handtype: str
    scoredcards: Hand
    allhandtypes: dict[str, list["PlayingCard"]]

    CHANCEOF: int
    CONSIDERED_FACE: set[str]
    CONSIDERED_SPADE: set[str]
    CONSIDERED_HEART: set[str]
    CONSIDERED_CLUB: set[str]
    CONSIDERED_DIAMOND: set[str]


class PlayingCard:
    suit: str
    value: str
    edition: str | None
    enhancement: str | None
    seal: str | None
    debuffed: bool
    hikerchips: int


class JokerCard:

    def __init__(self, game: Session, edition: None | str,
                 attr: list[str]) -> None:
        self.game = game
        self.edition = edition
        self.name: str

        self.debuffed = False
        self.broken = False

    def chipmult_pre(self):
        self.pre = str(self.game.chipmult)

    def chipmult_post(self, copy_level: int, text: str = ""):
        string = "(Copied) " if copy_level else ""
        string += str(self) + ": "
        ljustby = 22 - len(draincolor(string))
        string += " " * ljustby + text
        ljustby = 53 - len(draincolor(string))
        string += " " * ljustby + f"{self.pre}\t-->\t{self.game.chipmult}"
        print(string)

    def eval_blindselected(self, copy_level: int = 0):
        ...

    def eval_rulechange(self, copy_level: int = 0):
        ...

    def eval_beforehand(self, copy_level: int = 0):
        ...

    def eval_played_card(self, card: PlayingCard, copy_level: int = 0):
        ...

    def eval_held_card(self, card: PlayingCard, copy_level: int = 0):
        ...

    def eval_afterhand(self, copy_level: int = 0):
        ...

    def eval_edition(self):
        if not self.edition: return
        pre = str(self.game.chipmult)
        if self.edition == "F": self.game.chipmult.pluschip(50)
        elif self.edition == "H": self.game.chipmult.plusmult(10)
        elif self.edition == "P": self.game.chipmult.multmult(1.5)
        string = f"{self} edition evaluation"
        ljust_by = 53 - len(draincolor(string))
        string += " " * ljust_by
        string += f"{pre}\t-->\t{self.game.chipmult}"
        print(string)

    def __str__(self) -> str:
        string = str(self.name)
        if self.edition:
            string += " (" + colorcode(EDITION_COLOR[self.edition])
            string += EDITION_FULL[self.edition] + COLORSTOP + ")"
        return string


class JokerNotFound(JokerCard):
    """generic joker"""
    name = "None"


#Page 1/10


class Joker(JokerCard):
    """+4 Mult"""
    name = "Joker"

    def eval_afterhand(self, copy_level: int = 0):
        self.chipmult_pre()
        self.game.chipmult.plusmult(4)
        self.chipmult_post(copy_level, "+4")


class SUIT_MULT_JOKER(JokerCard):
    """super class for the four suit Mult jokers"""
    name: str

    def eval_beforehand(self, copy_level: int = 0):
        self.SUITCHARS: set[str]

    def eval_played_card(self, card: PlayingCard, copy_level: int = 0):
        if card.enhancement != "W" and card.suit not in self.SUITCHARS: return

        self.chipmult_pre()
        self.game.chipmult.plusmult(4)
        self.chipmult_post(copy_level, "+4")


class GreedyJoker(SUIT_MULT_JOKER):
    """Played cards with Diamond suit give +4 Mult when scored"""
    name = "Greedy Joker"

    def eval_beforehand(self, copy_level: int = 0):
        self.SUITCHARS = self.game.CONSIDERED_DIAMOND


class LustyJoker(SUIT_MULT_JOKER):
    """Played cards with Heart suit give +4 Mult when scored"""
    name = "Lusty Joker"

    def eval_beforehand(self, copy_level: int = 0):
        self.SUITCHARS = self.game.CONSIDERED_HEART


class WrathfulJoker(SUIT_MULT_JOKER):
    """Played cards with Spade suit give +4 Mult when scored"""
    name = "Wrathful Joker"

    def eval_beforehand(self, copy_level: int = 0):
        self.SUITCHARS = self.game.CONSIDERED_SPADE


class GluttonousJoker(SUIT_MULT_JOKER):
    """Played cards with Club suit give +4 Mult when scored"""
    name = "Gluttonous Joker"

    def eval_beforehand(self, copy_level: int = 0):
        self.SUITCHARS = self.game.CONSIDERED_CLUB


class PLUSMULT_HAND_JOKER(JokerCard):
    """super class for the five hand type jokers"""
    name: str

    def eval_beforehand(self, copy_level: int = 0):
        self.HANDTYPE: str
        self.plusmult: int

    def eval_afterhand(self, copy_level: int = 0):
        if not self.HANDTYPE in self.game.allhandtypes: return

        self.chipmult_pre()
        self.game.chipmult.plusmult(self.plusmult)
        self.chipmult_post(copy_level, color_cm(self.plusmult, 1))


class JollyJoker(PLUSMULT_HAND_JOKER):
    """+8 Mult if played hand contains a Pair"""
    name = "Jolly Joker"

    def eval_beforehand(self, copy_level: int = 0):
        self.HANDTYPE = "pair"
        self.plusmult = 8


class ZanyJoker(PLUSMULT_HAND_JOKER):
    """+12 Mult if played hand contains a Three of a kind"""
    name = "Zany Joker"

    def eval_beforehand(self, copy_level: int = 0):
        self.HANDTYPE = "three of a kind"
        self.plusmult = 12


class MadJoker(PLUSMULT_HAND_JOKER):
    """+20 Mult if played hand contains a Four of a kind"""
    name = "Mad Joker"

    def eval_beforehand(self, copy_level: int = 0):
        self.HANDTYPE = "four of a kind"
        self.plusmult = 20


class CrazyJoker(PLUSMULT_HAND_JOKER):
    """+12 Mult if played hand contains a Straight"""
    name = "Crazy Joker"

    def eval_beforehand(self, copy_level: int = 0):
        self.HANDTYPE = "straight"
        self.plusmult = 12


class DrollJoker(PLUSMULT_HAND_JOKER):
    """+10 Mult if played hand contains a Flush"""
    name = "Droll Joker"

    def eval_beforehand(self, copy_level: int = 0):
        self.HANDTYPE = "flush"
        self.plusmult = 10


class PLUSCHIP_HAND_JOKER(JokerCard):
    """super class for the five hand type jokers"""
    name: str

    def eval_beforehand(self, copy_level: int = 0):
        self.HANDTYPE: str
        self.pluschip: int

    def eval_afterhand(self, copy_level: int = 0):
        if not self.HANDTYPE in self.game.allhandtypes: return

        self.chipmult_pre()
        self.game.chipmult.pluschip(self.pluschip)
        self.chipmult_post(copy_level, color_cm(self.pluschip, 0))


class SlyJoker(PLUSCHIP_HAND_JOKER):
    """+50 Chips if played hand contains a Pair"""
    name = "Sly Joker"

    def eval_beforehand(self, copy_level: int = 0):
        self.HANDTYPE = "pair"
        self.pluschip = 50


class WilyJoker(PLUSCHIP_HAND_JOKER):
    """+100 Chips if played hand contains a Three of a kind"""
    name = "Wily Joker"

    def eval_beforehand(self, copy_level: int = 0):
        self.HANDTYPE = "three of a kind"
        self.pluschip = 100


class CleverJoker(PLUSCHIP_HAND_JOKER):
    """+150 Chips if played hand contains a Four of a kind"""
    name = "Clever Joker"

    def eval_beforehand(self, copy_level: int = 0):
        self.HANDTYPE = "four of a kind"
        self.pluschip = 150


class DeviousJoker(PLUSCHIP_HAND_JOKER):
    """+100 Chips if played hand contains a Straight"""
    name = "Devious Joker"

    def eval_beforehand(self, copy_level: int = 0):
        self.HANDTYPE = "straight"
        self.pluschip = 100


class CraftyJoker(PLUSCHIP_HAND_JOKER):
    """+80 Chips if played hand contains a Flush"""
    name = "Crafty Joker"

    def eval_beforehand(self, copy_level: int = 0):
        self.HANDTYPE = "flush"
        self.pluschip = 80


#Page 2/10


class HalfJoker(JokerCard):
    """+20 Mult if played hand contains 3 or fewer cards"""
    name = "Half Joker"

    def eval_afterhand(self, copy_level: int = 0):
        if len(self.game.playedhand) > 3: return

        self.chipmult_pre()
        self.game.chipmult.plusmult(20)
        self.chipmult_post(copy_level, f"+20")


class JokerStencil(JokerCard):
    """X1 Mult for each empty Joker slot
    Joker Stencil included"""

    def __init__(self, game: Session, edition: None | str,
                 attr: list[str]) -> None:
        raise NotImplementedError()


class FourFingers(JokerCard):
    """All Flushes and Straights can be made with 4 cards"""
    name = "Four Fingers"

    def eval_rulechange(self, copy_level: int = 0):
        self.game.straightflushsize = 4


class Mime(JokerCard):
    """Retrigger all card held in hand abilities"""
    name = "Mime"

    def eval_beforehand(self, copy_level: int = 0):
        for i, _ in enumerate(self.game.heldhand.retriggers):
            self.game.heldhand.retriggers[i] += 1


class CreditCard(JokerCard):
    """Go up to -$20 in debt"""

    name = "Credit Card"

    def foo():
        raise NotImplementedError("money")


class CeremonialDagger(JokerCard):
    """When BLind is selected, destroy Joker to the right and permanently add double its sell value to this Mult"""

    name = "Ceremonial Dagger"

    def __init__(self, game: Session, edition: None | str,
                 attr: list[str]) -> None:
        super().__init__(game, edition, attr)
        if attr: self.mult = int(attr[0])
        else: self.mult = 0

    def eval_blindselected(self, copy_level: int = 0):
        raise NotImplementedError("copy nextjoker code from blueprint")


class Banner(JokerCard):
    """+40 Chips for each remaining discard"""
    name = "Banner"

    def eval_afterhand(self, copy_level: int = 0):
        chips = 40 * (self.game.discards)
        if not chips: return
        self.chipmult_pre()
        self.game.chipmult.pluschip(chips)
        self.chipmult_post(copy_level, color_cm(chips, 0))


class MysticSummit(JokerCard):
    """+15 Mult when 0 discards remaining"""
    name = "Mystic Summit"

    def eval_afterhand(self, copy_level: int = 0):
        if self.game.discards: return
        self.chipmult_pre()
        self.game.chipmult.plusmult(15)
        self.chipmult_post(copy_level, color_cm(15, 0))


class MarbleJoker(JokerCard):
    """Adds one Stone card to deck when Blind is selected"""
    name = "Marble Joker"

    def foo():
        raise NotImplementedError()


class LoyaltyCard(JokerCard):
    """X4 Mult every 6 hands played"""
    name = "Loyalty Card"

    def __init__(self, game: Session, edition: None | str,
                 attr: list[str]) -> None:
        super().__init__(game, edition, attr)
        if attr: self.handsleft = int(attr[0])
        else: self.handsleft = 5

    def eval_afterhand(self, copy_level: int = 0):

        if not self.handsleft:
            self.chipmult_pre()
            self.game.chipmult.multmult(4)
            self.chipmult_post(copy_level, "X4")

        if not copy_level:
            self.handsleft -= 1
            self.handsleft %= 6

    def __str__(self) -> str:
        string = super().__str__()
        string += f" ({self.handsleft} remaining)"
        return string


class EightBall(JokerCard):
    """Create a Planet card if played hand contains 2 or more 8s
    (Must have room)"""
    name = "8 Ball"

    def eval_afterhand(self, copy_level: int = 0):
        raise NotImplementedError("no planets card yet")


class Misprint(JokerCard):
    """+23#@11D"""
    name = "Misprint"

    def eval_afterhand(self, copy_level: int = 0):
        self.chipmult_pre()
        plusmult = randint(0, 23)
        self.game.chipmult.plusmult(plusmult)
        self.chipmult_post(copy_level, f"+{plusmult}")


#class Dusk(JokerCard):
#Retrigger all played cards in final hand of round


class RaisedFist(JokerCard):
    """Adds double the rank of lowest card held in hand to Mult"""
    name = "Raised Fist"

    def eval_afterhand(self, copy_level: int = 0):
        valuecards = [
            card for card in self.game.heldhand.cards
            if not card.enhancement == "R"
        ]
        if not valuecards: return
        lowestrank = min([VALUESCORE[card.value] for card in valuecards])
        self.chipmult_pre()
        self.game.chipmult.plusmult(lowestrank * 2)
        self.chipmult_post(copy_level, text=f"+2X{lowestrank}")


#class ChaosTheClown(JokerCard):
#1 free Reroll per shop

#Page 3/10

#class Fibonacci(JokerCard):
#Each played Ace, 2, 3, 5, or 8 gives +8 Mult when scored


class SteelJoker(JokerCard):
    """This Joker gains X0.25 Mult for each Steel Card in your full deck"""
    name = "Steel Joker"

    def __init__(self, game: Session, edition: None | str,
                 attr: list[str]) -> None:
        super().__init__(game, edition, attr)
        if attr:
            raise AssertionError(
                "to account for disappearance of steel cards," +
                " such as getting sucked by a vampire," +
                " steel joker counts the steel card count in real time" +
                " rather than with an attribute\nplease add the" +
                " right amount of cards with steel enhancements under 'deck:' instead"
            )

    def eval_afterhand(self, copy_level: int = 0):
        multmult = self.steel_mult()
        self.chipmult_pre()
        self.game.chipmult.multmult(multmult)
        self.chipmult_post(copy_level)

    def steel_mult(self) -> float:
        allcards = self.game.deck.cards + self.game.totalhand.cards
        steelcount = len([c for c in allcards if c.enhancement == "S"])
        return 1. + steelcount * .25

    def __str__(self) -> str:
        string = super().__str__()
        string += f" ({color_cm(self.steel_mult(),2)})"
        return string


#class ScaryFace(JokerCard):
"""Played face cards give +30 Chips when scored"""


class AbstractJoker(JokerCard):
    """+3 Mult for each Joker card"""
    name = "Abstract Joker"

    def eval_afterhand(self, copy_level: int = 0):
        self.chipmult_pre()
        plusmult = 3 * len(self.game.jokers)
        self.game.chipmult.plusmult(plusmult)
        self.chipmult_post(copy_level)

    def __str__(self) -> str:
        string = super().__str__()
        plusmult = 3 * len(self.game.jokers)
        string += f" ({color_cm(plusmult, 1)})"
        return string


#class DelayedGratification(JokerCard):
#Earn $2 per discard if no discards are used by the end of the round


class Hack(JokerCard):
    """Retrigger each played 2, 3, 4, or 5"""
    name = "Hack"

    def eval_beforehand(self, copy_level: int = 0):
        for i, card in enumerate(self.game.scoredcards.cards):
            if card.value in ("2", "3", "4", "5"):
                self.game.scoredcards.retriggers[i] += 1


class Pareidolia(JokerCard):
    """All cards are considered face cards"""
    name = "Pareidolia"

    def eval_rulechange(self, copy_level: int = 0):
        self.game.CONSIDERED_FACE = set(VALUES.keys())


class GrosMichel(JokerCard):
    """+15 Mult
    1 in 4 chance this card is destroyed at end of round"""
    name = "Gros Michel"

    def eval_afterhand(self, copy_level: int = 0):
        self.chipmult_pre()
        self.game.chipmult.plusmult(15)
        self.chipmult_post(copy_level, "+15")

        if copy_level: return
        if randint(1, 4) <= self.game.CHANCEOF:
            print(f"{self}: Extinct!")
            self.broken = True
        else:
            print(f"{self}: Safe!")


class EvenSteven(JokerCard):
    """Played cards with even rank give +4 Mult when scored
    (10, 8, 6, 4, 2)"""
    name = "Even Steven"
    even_vals = {str(i) for i in range(2, 11, 2)}

    def eval_played_card(self, card: PlayingCard, copy_level: int = 0):
        if not card.value in self.even_vals: return
        self.chipmult_pre()
        self.game.chipmult.plusmult(4)
        self.chipmult_post(copy_level, color_cm(4, 1))


class OddTodd(JokerCard):
    """Played cards with odd rank give +30 Chips when scored
    (A, 9, 7, 5, 3)"""
    name = "Odd Todd"
    odd_vals = {str(i) for i in range(3, 11, 2)}.union({"A"})

    def eval_played_card(self, card: PlayingCard, copy_level: int = 0):
        if not card.value in self.odd_vals: return
        self.chipmult_pre()
        self.game.chipmult.pluschip(30)
        self.chipmult_post(copy_level, color_cm(30, 0))


class Scholar(JokerCard):
    """Played Aces give +20 Chips and +4 Mult when scored"""
    name = "Scholar"

    def eval_played_card(self, card: PlayingCard, copy_level: int = 0):
        if not card.value == "A": return
        self.chipmult_pre()
        self.game.chipmult.pluschip(20)
        self.game.chipmult.plusmult(4)
        text = f"{color_cm(20, 0)} {color_cm(4,1)}"
        self.chipmult_post(copy_level, text)


#class BusinessCard(JokerCard):
#Played face cards have a 1 in 2 chance to give $2 when scored

#class Supernova(JokerCard):
#Adds the number of times poker hand has been played to Mult

#class RideTheBus(JokerCard):
#+1 Mult per consecutive hand played without a scoring face card

#class SpaceJoker(JokerCard):
#1 in 4 chance to upgrade level of played poker hand

#Page 4/10

#class Egg(JokerCard):
#Gains $3 of sell value at end of round


class Burglar(JokerCard):
    """When Blind is selected, gain +3 Hands and lose all discards"""
    name = "Burglar"

    def eval_blindselected(self, copy_level: int = 0):
        self.game.discards = 0
        self.game.handcount += 3


#class Blackboard(JokerCard):
#X3 Mult if all cards held in hand are Spades or Clubs

#class Runner(JokerCard):
#Gains +10 Chips if played hand contains a Straight
# it starts at 20

#class IceCream(JokerCard):
#+100 Chips \n -5 Chips for every hand played

#class DNA(JokerCard):
#If first hand of round has only 1 card, add a permanent copy to deck and draw it to hand

#class Splash(JokerCard):
#Every played card counts in scoring

#class BlueJoker(JokerCard):
#+2 Chips for each remaining card in deck

#class SixthSense(JokerCard):
"""If first hand of round is a single 6, destroy it and create a Spectral card
(Must have room)"""

#class Constellation(JokerCard):
#Gains X0.1 Mult per Planet card used

#class Hiker(JokerCard):
#Every played card permanently gains +4 Chips when scored

#class FacelessJoker(JokerCard):
#Earn $5 if 3 or more face cards are discarded at the same time


class GreenJoker(JokerCard):
    """+1 Mult per hand played
    -1 Mult per discard"""
    name = "Green Joker"

    def __init__(self, game: Session, edition: None | str,
                 attr: list[str]) -> None:
        super().__init__(game, edition, attr)
        if attr: self.mult = int(attr[0])
        else: self.mult = 0

    def eval_beforehand(self, copy_level: int = 0):
        if not copy_level: self.mult += 1

    def eval_afterhand(self, copy_level: int = 0):
        self.chipmult_pre()
        self.game.chipmult.plusmult(self.mult)
        self.chipmult_post(copy_level)

    def __str__(self) -> str:
        string = super().__str__()
        string += f" ({color_cm(self.mult, 1)})"
        return string


#class Superposition(JokerCard):
#"""Create a Tarot card if poker hand contains an Ace and a Straight
#(Must have room)"""

#class ToDoList(JokerCard):
#Earn $5 if poker hand is a %s, poker hand changes on every payout

#Page 5/10


class Cavendish(JokerCard):
    """X3 Mult
    1 in 1000 chance this card is destroyed at end of round"""
    name = "Cavendish"

    def eval_afterhand(self, copy_level: int = 0):
        pre = str(self.game.chipmult)
        self.game.chipmult.multmult(3)
        string = "(Blueprint) " if copy_level else ""
        string += "Cavendish X3"
        string = string.ljust(53) + f"{pre}\t-->\t{self.game.chipmult}"

        print(string)

        if copy_level: return
        if randint(1, 1000) <= self.game.CHANCEOF:
            print(f"{self}: Extinct!")
            self.broken = True
        else:
            print(f"{self}: Safe!")


#class CardSharp(JokerCard):
#X3 Mult if played poker hand has already been played this round


class RedCard(JokerCard):
    """Gains +3 Mult when any Booster Pack is skipped"""
    name = "Red Card"

    def __init__(self, game: Session, edition: None | str,
                 attr: list[str]) -> None:
        raise NotImplementedError("just haven't")


class Madness(JokerCard):
    """When Blind is selected, gain X0.5 Mult and destroy a random Joker"""
    name = "Madness"

    def __init__(self, game: Session, edition: None | str,
                 attr: list[str]) -> None:
        super().__init__(game, edition, attr)
        if attr: self.mult = float(attr[0])
        else: self.mult = 1.0

    def eval_afterhand(self, copy_level: int = 0):
        pre = str(self.game.chipmult)
        self.game.chipmult.multmult(self.mult)
        string = "(Blueprint) " if copy_level else ""
        string += "Madness multmult"
        string = string.ljust(53) + f"{pre}\t-->\t{self.game.chipmult}"
        print(string)

    def __str__(self) -> str:
        string = super().__str__()
        string += f" ({color_cm(self.mult, 2)})"
        return string


class SquareJoker(JokerCard):
    """Gains +4 Chips if played hand has exactly 4 cards"""
    name = "Square Joker"

    def __init__(self, game: Session, edition: None | str,
                 attr: list[str]) -> None:
        super().__init__(game, edition, attr)
        if attr: self.chips = int(attr[0])
        else: self.chips = 16

    def eval_beforehand(self, copy_level: int = 0):
        if copy_level: return
        if len(self.game.playedhand) == 4:
            self.chips += 4

    def eval_afterhand(self, copy_level: int = 0):
        self.game.chipmult.pluschip(self.chips)

    def __str__(self) -> str:
        string = super().__str__()
        string += f" ({color_cm(self.chips, 0)})"
        return string


class Seance(JokerCard):
    """If poker hand is a Straight Flush, create a random Spectral card
    (Must have room)"""
    name = "Séance"

    def eval_beforehand(self, copy_level: int = 0):
        if self.game.handtype == "straight flush":
            raise NotImplementedError(
                "tarot/spectral/planet cards not implemented yet")


class RiffRaff(JokerCard):
    """When Blind is selected, create 2 Common Jokers
    (Must have room)"""
    name = "Riff-Raff"

    def eval_blindselected(self, copy_level: int = 0):
        raise NotImplementedError(self.name)


class Vampire(JokerCard):
    """Gains X0.2 Mult per Enhanced card played, removes card Enhancement"""
    name = "Vampire"

    def __init__(self, game: Session, edition: None | str,
                 attr: list[str]) -> None:
        super().__init__(game, edition, attr)
        if attr: self.mult = float(attr[0])
        else: self.mult = 1.0

    def eval_beforehand(self, copy_level: int = 0):
        if copy_level: return
        for i, card in enumerate(self.game.scoredcards.cards):
            if card.enhancement:
                card.enhancement = None
                self.mult = round(self.mult + 0.2, 1)

    def eval_afterhand(self, copy_level: int = 0):
        self.chipmult_pre()
        self.game.chipmult.multmult(self.mult)
        self.chipmult_post(copy_level)

    def __str__(self) -> str:
        string = super().__str__()
        string += f" ({color_cm(self.mult, 2)})"
        return string


#class SHortcut
#Allows Straights to be made with gaps of 1 rank
#(ex: 2 3 5 7 8)

#Hologram
#Gains X0.25 Mult per playing card added to your deck

#Vagabond


class Baron(JokerCard):
    """#TODO"""
    name = "Baron"

    def eval_beforehand(self, copy_level: int = 0):
        for i, card in enumerate(self.game.heldhand.cards):
            if card.value != "K" or card.enhancement != "S": continue
            self.game.heldhand.retriggers[i] += 1


#CloudNine

#Rocket

#Obelisk

#Page 6/10


class MidasMask(JokerCard):
    """All face cards become Gold cards when played"""
    name = "Midas Mask"

    def eval_beforehand(self, copy_level: int = 0):
        for i, card in enumerate(self.game.scoredcards.cards):
            if card.value in self.game.CONSIDERED_FACE:
                card.enhancement = "O"


#Page 7/10


class WalkieTalkie(JokerCard):
    """Each played 10 or 4 gives +10 Chips and +4 Mult when scored"""
    name = "Walkie Talkie"

    def eval_played_card(self, card: PlayingCard, copy_level: int = 0):
        if card.value not in ("4", "10"): return
        self.chipmult_pre()
        self.game.chipmult.pluschip(10)
        self.game.chipmult.plusmult(4)
        self.chipmult_post(copy_level)


#Page 8/10


class SockAndBuskin(JokerCard):
    """Retrigger all played face cards"""
    name = "Sock and Buskin"

    def eval_beforehand(self, copy_level: int = 0):
        for i, card in enumerate(self.game.scoredcards.cards):
            if card.value in self.game.CONSIDERED_FACE:
                self.game.scoredcards.retriggers[i] += 1


class SmearedJoker(JokerCard):
    """Hearts and Diamonds count as the same suit, Spades and Clubs count as the same suit"""
    name = "Smeared Joker"

    def eval_beforehand(self, copy_level: int = 0):
        h, d = self.game.CONSIDERED_HEART, self.game.CONSIDERED_DIAMOND
        self.game.CONSIDERED_HEART = h.union(d)
        self.game.CONSIDERED_DIAMOND = h.union(d)
        s, c = self.game.CONSIDERED_CLUB, self.game.CONSIDERED_SPADE
        self.game.CONSIDERED_CLUB = s.union(c)
        self.game.CONSIDERED_SPADE = s.union(c)
        print("H/D and S/C are pairwise smeared together")


#Throwback
#X0.25 Mult for each Blind skipped this run


class HangingChad(JokerCard):
    """Retrigger first played card used in scoring"""
    name = "Hanging Chad"

    def eval_beforehand(self, copy_level: int = 0):
        self.game.scoredcards.retriggers[0] += 2



#RoughGem

class Bloodstone(JokerCard):
    name = "Bloodstone"

    def eval_played_card(self, card: PlayingCard, copy_level: int = 0):
        if not (card.suit in self.game.CONSIDERED_HEART): return
        if randint(1, 2) <= self.game.CHANCEOF:
            self.chipmult_pre()
            self.game.chipmult.multmult(1.5)
            self.chipmult_post(copy_level)


#Arrowhead
#OnyxAgate


class GlassJoker(JokerCard):
    """#TODO"""
    name = "Glass Joker"

    def __init__(self, game: Session, edition: None | str,
                 attr: list[str]) -> None:
        super().__init__(game, edition, attr)
        if attr: self.mult = float(attr[0])
        else: self.mult = 1.0

    #TODO: increase when glass breaks

    def __str__(self) -> str:
        string = super().__str__()
        string += f" ({color_cm(self.mult, 2)})"
        return string


#Page 9/10

#Showman
#FlowerPot


class Blueprint(JokerCard):
    """Copies ability of Joker to the right"""
    name = "Blueprint"

    def __init__(self, game: Session, edition: None | str,
                 attr: list[str]) -> None:
        super().__init__(game, edition, attr)
        self.nextjoker = None

    def eval_beforehand(self, copy_level=0):
        i = self.game.jokers.index(self)
        if i == len(self.game.jokers):
            self.nextjoker = JokerNotFound(self.game, None, None)
            return
        if copy_level > 1:
            raise RecursionError("you know what you did")
        self.nextjoker: JokerCard = self.game.jokers[i + 1]
        if not copy_level: print(f"Blueprint is copying {self.nextjoker}")
        self.nextjoker.eval_beforehand(copy_level=copy_level + 1)

    def eval_played_card(self, card: PlayingCard, copy_level=0):
        self.nextjoker.eval_played_card(card, copy_level=copy_level + 1)

    def eval_afterhand(self, copy_level=0):
        self.nextjoker.eval_afterhand(copy_level=copy_level + 1)

    def __str__(self) -> str:
        string = super().__str__()
        if self.nextjoker: string += f" (copying {self.nextjoker})"
        return string


#wee joker
#merry andy


class OopsAll6s(JokerCard):
    """Doubles all listed probabilities
    (ex: 1 in 3 -> 2 in 3)"""
    name = "Oops! All 6s"

    def eval_rulechange(self, copy_level: int = 0):
        self.game.CHANCEOF *= 2


#idol
#seeing double
#matador


class HitTheRoad(JokerCard):
    """Gains X0.5 Mult per discarded Jack this round"""
    name = "Hit the Road"

    def __init__(self, game: Session, edition: None | str,
                 attr: list[str]) -> None:
        super().__init__(game, edition, attr)
        if attr: self.mult = float(attr[0])
        else: self.mult = 1.0

    def discard():
        raise NotImplementedError()


class MULTMULT_HAND_JOKER(JokerCard):
    """super class for the five hand type jokers"""
    name: str

    def eval_beforehand(self, copy_level: int = 0):
        self.HANDTYPE: str
        self.multby: int

    def eval_afterhand(self, copy_level: int = 0):
        if not self.HANDTYPE in self.game.allhandtypes: return

        self.chipmult_pre()
        self.game.chipmult.multmult(self.multby)
        self.chipmult_post(copy_level, f"X{self.multby}")


class TheDuo(MULTMULT_HAND_JOKER):
    """X2 Mult if played hand contains a Pair"""
    name = "The Duo"

    def eval_beforehand(self, copy_level: int = 0):
        self.HANDTYPE = "pair"
        self.multby = 2


class TheTrio(MULTMULT_HAND_JOKER):
    """X3 Mult if played hand contains a Three of a kind"""
    name = "The Trio"

    def eval_beforehand(self, copy_level: int = 0):
        self.HANDTYPE = "three of a kind"
        self.multby = 3


class TheFamily(MULTMULT_HAND_JOKER):
    """X4 Mult if played hand contains a Four of a kind"""
    name = "The Family"

    def eval_beforehand(self, copy_level: int = 0):
        self.HANDTYPE = "four of a kind"
        self.multby = 4


class TheOrder(MULTMULT_HAND_JOKER):
    """X3 Mult if played hand contains a Straight"""
    name = "The Order"

    def eval_beforehand(self, copy_level: int = 0):
        self.HANDTYPE = "straight"
        self.multby = 3


class TheTribe(MULTMULT_HAND_JOKER):
    """X2 Mult if played hand contains a Flush"""
    name = "The Tribe"

    def eval_beforehand(self, copy_level: int = 0):
        self.HANDTYPE = "flush"
        self.multby = 2


#Page 10/10

#stunt guy
#invisible


class Brainstorm(JokerCard):
    """Copies the ability of leftmost Joker"""
    name = "Brainstorm"

    def __init__(self, game: Session, edition: None | str,
                 attr: list[str]) -> None:
        super().__init__(game, edition, attr)
        self.leftestjoker = None

    def eval_beforehand(self, copy_level=0):
        self.leftestjoker: JokerCard = self.game.jokers[0]
        if self.leftestjoker is self:
            self.leftestjoker = JokerNotFound(self.game, None, None)
            return
        if not copy_level: print(f"Brainstorm is copying {self.leftestjoker}")
        self.leftestjoker.eval_beforehand(copy_level=copy_level + 1)

    def eval_played_card(self, card: PlayingCard, copy_level=0):
        self.leftestjoker.eval_played_card(card, copy_level=copy_level + 1)

    def eval_held_card(self, card: PlayingCard, copy_level=0):
        self.leftestjoker.eval_held_card(card, copy_level=copy_level + 1)

    def eval_afterhand(self, copy_level=0):
        self.leftestjoker.eval_afterhand(copy_level=copy_level + 1)

    def __str__(self) -> str:
        string = super().__str__()
        if self.leftestjoker: string += f" (copying {self.leftestjoker})"
        return string


#satellite


class ShootTheMoon(JokerCard):
    """+13 Mult for each Queen held in hand"""
    name = "Shoot The Moon"

    def eval_held_card(self, card: PlayingCard, copy_level: int = 0):
        if card.value != "Q": return
        self.chipmult_pre()
        self.game.chipmult.plusmult(13)
        self.chipmult_post(copy_level)


class DriversLicense(JokerCard):
    """X3 Mult if you have at least 16 Enhanced cards in your full deck"""
    name = "Driver's License"

    def eval_afterhand(self, copy_level: int = 0):
        allcards = self.game.deck.cards + self.game.totalhand.cards
        if len([c for c in allcards if c.enhancement]) < 16: return
        self.chipmult_pre()
        self.game.chipmult.multmult(3)
        self.chipmult_post(copy_level)


#cartomancer
"""Create a Tarot card when Blind is selected
(Must have room)"""

#astronomer
"""All Planet cards and Celestial Packs in the shop are free"""

#burntjoker
"""Upgrade the level of the first discarded poker hand each round"""

#bootstraps
"""+2 Mult for every $5 you have"""


#?
#?
#?
#?
class Perkeo(JokerCard):
    """Creates a Negative copy of 1 random consumable card in your possession at the end of the shop"""

    def __init__(self, game: Session, edition: None | str,
                 attr: list[str]) -> None:
        raise NotImplementedError("perkeo")


JOKER_IDS: dict[int, JokerCard] = {
    0: JokerNotFound,
    1: Joker,
    2: GreedyJoker,
    3: LustyJoker,
    4: WrathfulJoker,
    5: GluttonousJoker,
    6: JollyJoker,
    7: ZanyJoker,
    8: MadJoker,
    9: CrazyJoker,
    10: DrollJoker,
    11: SlyJoker,
    12: WilyJoker,
    13: CleverJoker,
    14: DeviousJoker,
    15: CraftyJoker,
    16: HalfJoker,
    #17: JokerStencil,
    18: FourFingers,
    19: Mime,
    20: CreditCard,
    21: CeremonialDagger,
    22: Banner,
    23: MysticSummit,
    25: LoyaltyCard,
    26: EightBall,
    27: Misprint,
    29: RaisedFist,
    32: SteelJoker,
    34: AbstractJoker,
    36: Hack,
    37: Pareidolia,
    38: GrosMichel,
    39: EvenSteven,
    40: OddTodd,
    41: Scholar,
    58: GreenJoker,
    61: Cavendish,
    63: RedCard,
    64: Madness,
    65: SquareJoker,
    66: Seance,
    67: RiffRaff,
    68: Vampire,
    72: Baron,
    76: MidasMask,
    101: WalkieTalkie,
    109: SockAndBuskin,
    113: SmearedJoker,
    115: HangingChad,
    117: Bloodstone,
    120: GlassJoker,
    123: Blueprint,
    126: OopsAll6s,
    130: HitTheRoad,
    131: TheDuo,
    132: TheTrio,
    133: TheFamily,
    134: TheOrder,
    135: TheTribe,
    138: Brainstorm,
    140: ShootTheMoon,
    141: DriversLicense,
}

JOKERS = {joker.name: joker for joker in JOKER_IDS.values()}
