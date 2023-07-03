import kasa
import asyncio

# async def test_strip(strip):
#     await strip.update()

#     print(strip.state_information)

#     for child in strip.children:
#         await child.turn_on()
#         await strip.update()

# strip = kasa.SmartStrip("192.168.11.15")
# asyncio.run(test_strip(strip))


async def test_plug(plug):
    await plug.update()

    print(plug.state_information)

    for _ in range(8):
        await plug.turn_on()
        await plug.update()
        await plug.turn_off()
        await plug.update()

plug = kasa.SmartPlug("192.168.11.49")
asyncio.run(test_plug(plug))
