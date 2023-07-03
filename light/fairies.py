import asyncio
import random

from utilities import *

async def fairies(lights):
    background_color = rgb(32, 32, 255)
    fairy_colors = [cold_white, warm_white]

    for light in lights:
        light.set_state(background_color)

    loop = PeriodicLoop(0.15)

    indices = [0, 1]
    while not loop.done():
        for i in range(len(indices)):
            lights[indices[i]].set_state(background_color)
            indices[i] = random.choice(list(neighbors[indices[i]]))
            lights[indices[i]].set_state(fairy_colors[i])
        await loop.next()
