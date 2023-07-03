import kasa
import yaml
import asyncio
import random

import time

with open("dimmers.yml", "r") as f:
    dimmer_ips = yaml.safe_load(f)

dimmers = [kasa.SmartPlug(ip) for _, ip in dimmer_ips.items()]
for d in dimmers:
    d.modules = {}

async def setd(device, state):
    if state:
        await device.turn_on()
    else:
        await device.turn_off()
    await device.update()

async def seti(i, state):
    await setd(dimmers[i % len(dimmers)], state)

async def init():
    for d in dimmers:
        await d.update()
        await setd(d, False)

    await asyncio.sleep(0.2)

interrupt_pattern_loop = False


class PeriodicLoop:

    def __init__(self, period, length=None):
        self.period = period
        self.next_frame_time = time.perf_counter()
        if length:
            self.finish_time = self.next_frame_time + length
        else:
            self.finish_time = None

    async def next(self):
        self.next_frame_time += self.period
        now = time.perf_counter()
        while now < self.next_frame_time and not interrupt_pattern_loop:
            await asyncio.sleep(0.005)
            now = time.perf_counter()

    def done(self):
        if interrupt_pattern_loop:
            return True
        if self.finish_time:
            return self.next_frame_time >= self.finish_time
        return False

async def wanderer():
    p = 0
    v = 1
    n = len(dimmers)

    loop = PeriodicLoop(0.15)

    for i in range(500):
        if random.random() < 0.3:
            v = -v
        if p + v < 0:
            v = 1
        if p + v >= n:
            v = -1
        await asyncio.gather(seti(p, False), seti(p + v, True))
        p += v

        await loop.next()

async def dasher():
    p = 0
    n = len(dimmers)

    loop = PeriodicLoop(1)

    while not loop.done():
        q = p
        while q == p:
            q = random.randrange(n)
        while p != q:
            v = 1 if p < q else -1
            await asyncio.gather(seti(p, False), seti(p + v, True))
            p += v
        await loop.next()


async def fill():
    p = 0
    n = len(dimmers)

    loop = PeriodicLoop(0.1)

    while not loop.done():
        for i in range(n):
            await seti(i, True)
            await loop.next()
        for i in range(4):
            await loop.next()
        for i in range(n):
            await seti(i, False)
            await loop.next()
        for i in range(4):
            await loop.next()


async def shots():
    p = 0
    n = len(dimmers)

    loop = PeriodicLoop(1)

    while not loop.done():
        p, v = random.choice([(-1, 1), (n, -1)])
        for i in range(n):
            await asyncio.gather(seti(p, False), seti(p + v, True))
            p += v
            await asyncio.sleep(0.05)
        await seti(p, False)
        await loop.next()

async def the_show():
    await init()
    await shots()

asyncio.run(the_show())
