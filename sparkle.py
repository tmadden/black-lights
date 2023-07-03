import asyncio
import time
import random
from colour import Color

from utilities import *

from operator import add


async def sparkle(lights):
    loop = PeriodicLoop(0.02)

    colors = [random.choice(snow_palette) for _ in range(24)]

    while not loop.done():
        for i in range(24):
            lights[i].set_state(colors[i])

        colors[random.randint(0, 23)] = random.choice(palettes[palette_index])

        for click in clicks():
            palette_index = (palette_index + 1) % len(palettes)
            colors = [random.choice(palettes[palette_index]) for _ in range(24)]

        await loop.next()
