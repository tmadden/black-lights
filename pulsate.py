import asyncio
import time
import random
from colour import Color

from utilities import *

from operator import add


async def pulsate(lights):
    colors = list(Color("red").range_to(Color("yellow"), 12))
    for i in range(4):
        colors.append(colors[-1])
    colors += list(Color("yellow").range_to(Color("red"), 12))
    for i in range(4):
        colors.append(colors[-1])

    while True:
        i = random.choice(range(6))
        j = i
        while i == j:
            j = random.choice(range(6))
        loop = PeriodicLoop(0.1)
        # for b in range(6):
        #     for k in [i, j]:
        #         lights[k].set_state(dim(color(colors[0]), b * 40))
        for c in colors:
            for k in [i, j]:
                lights[k].set_state(color(c))
            await loop.next()
        # for b in range(6):
        #     for k in [i, j]:
        #         lights[k].set_state(dim(color(colors[-1]), 255 - b * 40))
        for k in [i, j]:
            lights[k].set_state(off)
