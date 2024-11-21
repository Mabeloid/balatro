from bal_common import *
from bal_session import Session

import os

DIR = os.path.dirname(__file__)


def main1():
    input_file = open(f"{DIR}/inputs.txt").read()
    game = Session(input_file)
    game.getscore()
    print(BOLD + "final score:", game.chipmult.scorestr() + COLORSTOP)

def main2():
    samples = 500

    input_file = open(f"{DIR}/inputs.txt").read()
    scores = []
    for _ in range(samples):
        game = Session(input_file)
        game.getscore()
        scores += [game.chipmult.score()]
    avgscore =  game.chipmult.format_e(sum(scores)/len(scores))
    os.system("cls")
    print(scores)
    print(f"Average score over {samples} simulations: {BOLD}{avgscore}{COLORSTOP}")

if __name__ == "__main__":
    main2()