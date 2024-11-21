from bal_common import *
from bal_chipmult import ChipMult

class Session:
    chipmult: ChipMult
    CHANCEOF: int

class PlayingCard:

    def __init__(self,
                 game: "Session",
                 suit: str,
                 value: str,
                 edition: str = None,
                 enhancement: str = None,
                 seal: str = None,
                 debuffed: bool = False,
                 hikerchips: int = 0) -> None:
        self.game = game
        self.suit = suit
        self.value = value
        self.edition = edition
        self.enhancement = enhancement
        self.seal = seal

        self.debuffed = debuffed
        self.broken = False
        self.hikerchips = hikerchips

    def __str__(self) -> str:
        color = SUITCOLOR[self.suit]
        string = colorcode(color) + self.suit + self.value

        optional = []
        if self.edition:
            optional.append(
                colorcode(EDITION_COLOR[self.edition]) +
                EDITION_FULL[self.edition])
        if self.enhancement:
            optional.append(
                colorcode(ENHANCEMENT_COLOR[self.enhancement]) +
                ENHANCEMENT_FULL[self.enhancement])
        if self.seal:
            optional.append(
                colorcode(SEAL_COLOR[self.seal]) + SEAL_FULL[self.seal])

        string += COLORSTOP

        if optional:
            innertext = f'{COLORSTOP}, '.join(optional)
            string += " (" + innertext + COLORSTOP + ")"
        return string

    def eval_played(self) -> None:
        if self.debuffed: return
        chipmult = self.game.chipmult
        chipmult.pluschip(VALUESCORE[self.value])
        chipmult.pluschip(self.hikerchips)

        if self.edition == "F": chipmult.pluschip(50)
        elif self.edition == "H": chipmult.plusmult(10)
        elif self.edition == "P": chipmult.multmult(1.5)

        if self.enhancement == "B": chipmult.pluschip(30)
        elif self.enhancement == "R": chipmult.pluschip(50)
        elif self.enhancement == "M": chipmult.plusmult(4)
        elif self.enhancement == "G":
            chipmult.multmult(2)
            if randint(1, 4) <= self.game.CHANCEOF:
                self.broken = True
        elif self.enhancement == "L":
            if randint(1, 5) <= self.game.CHANCEOF:
                chipmult.multmult(1.5)
            elif randint(1, 15) <= self.game.CHANCEOF:
                self.game.money += 20

        if self.seal == "G": self.game.money += 3


    def eval_held(self):
        chipmult = self.game.chipmult

        if self.enhancement == "S":
            #self.chipmult_pre()
            chipmult.multmult(1.5)
            #self.chipmult_post("Steel mult")
        elif self.enhancement == "O":
            self.game.money += 5
    
    def chipmult_pre(self):
        self.pre = str(self.game.chipmult)

    def chipmult_post(self, text: str = ""):
        string = str(self) + ": "
        ljustby = 22 - len(draincolor(string))
        string += " " * ljustby + text
        ljustby = 53 - len(draincolor(string))
        string += " " * ljustby + f"{self.pre}\t-->\t{self.game.chipmult}"
        print(string)