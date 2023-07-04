import kasa
import yaml
import asyncio
import random

from utilities import PeriodicLoop

dimmers = []

async def init(dimmer_ips):
    global dimmers
    dimmers = [kasa.SmartPlug(ip) for _, ip in dimmer_ips.items()]
    for d in dimmers:
        d.modules = {}

    for d in dimmers:
        await d.update()
        await setd(d, False)

    await asyncio.sleep(0.2)

async def setd(device, state):
    if not state:
        await device.turn_on()
    else:
        await device.turn_off()
    await device.update()

async def seti(i, state):
    await setd(dimmers[i % len(dimmers)], state)


async def all_on():
    n = len(dimmers)

    loop = PeriodicLoop(0.15)

    while not loop.done():
        for i in range(n):
            await seti(i, True)
        await loop.next()


async def wanderer():
    p = 0
    v = 1
    n = len(dimmers)

    loop = PeriodicLoop(0.15)

    while not loop.done():
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

    loop = PeriodicLoop(6)

    while not loop.done():
        q = p
        while abs(q - p) < 2:
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
    n = len(dimmers)

    loop = PeriodicLoop(1)

    while not loop.done():
        l = 2
        p, v = random.choice([(-l, 1), (n, -1)])
        for i in range(n):
            await asyncio.gather(seti(p, False), seti(p + v, True))
            p += v
            await asyncio.sleep(0.05)
        await seti(p, False)
        await loop.next()
