from bal_common import *


class ChipMult(list):

    def __init__(self,
                 chipmult: tuple[int, int] = (0, 0),
                 need_score: int = 0):
        self.chip = chipmult[0]
        self.mult = chipmult[1]
        self.need_score = need_score

    def pluschip(self, chip: int):
        self.chip += chip

    def plusmult(self, mult: int):
        self.mult += mult

    def multmult(self, mult: int | float):
        self.mult *= mult

    def score(self) -> int:
        return int(self.chip * self.mult)

    def format_e(self, number: int | float) -> str:
        if number < 100_000_000_000:
            string = "{:,}".format(number)
            if "." in string: string = string.rstrip("0").rstrip(".")
        elif number >= 1.8e308: string = "naneinf"
        else: string = "{:.3e}".format(number).replace("+", "")
        return string

    def scorestr(self) -> str:
        return self.format_e(self.score())

    def __str__(self) -> str:
        string = colorcode(COMMON_COLORS["chip"]) + self.format_e(self.chip)
        string += COLORSTOP + " X "
        string += colorcode(COMMON_COLORS["mult"]) + self.format_e(
            round(self.mult, 2))
        string += COLORSTOP + " = " + self.format_e(self.score())
        return string

    def whitestr(self) -> str:
        string = f"{self.chip} X {self.mult} = {self.scorestr()}"
        return string


if __name__ == "__main__":
    cm = ChipMult((1, 1))
    for _ in range(15):
        cm.multmult(10)
        print(cm)
