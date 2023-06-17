import kasa
import asyncio

async def test_strip(strip):
    await strip.update()

    print(strip.state_information)

    for child in strip.children:
        await child.turn_off()
        await strip.update()

strip = kasa.SmartStrip("192.168.11.15")
asyncio.run(test_strip(strip))
