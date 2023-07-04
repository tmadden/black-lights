import yaml
import asyncio
import time
import random

from utilities import reset_all, the_palettes
import utilities

from wiz import Light

import discover
from sparkle import sparkle
from pulsate import pulsate
from light.fairies import fairies

import dark

test_pattern = fairies

all_patterns = [pulsate]

current_pattern_index = 0
current_palette_index = 0


async def control_loop(lights):
    global current_pattern_index

    while True:
        utilities.interrupt_pattern_loop = False
        utilities.mouse_clicks.clear()
        if test_pattern:
            await test_pattern(lights)
        else:
            await all_patterns[current_pattern_index](lights)


async def main():

    with open("dimmers.yml", "r") as f:
        dimmer_ips = yaml.safe_load(f)
    # print("discovering kasa lights...")
    # dimmer_ips = {}
    # while len(dimmer_ips) != 6:
    #     dimmer_ips = await discover.discover_kasa()
    await dark.init(dimmer_ips)

    with open("ips.yml", "r") as file:
        ips = yaml.safe_load(file)
    ip = ips[:6]
    # print("discovering wiz lights...")
    # ips = []
    # while len(ips) != 6:
    #     ips = await discover.discover_wiz()
    lights = [Light(ip) for ip in ips]
    print("initializing wiz lights...")
    await asyncio.gather(*[light.connect() for light in lights])

    utilities.set_active_palette(the_palettes[0])

    print("control loop...")
    await asyncio.gather(control_loop(lights), dark.dasher(),
                         *[light.comm_loop() for light in lights])


from pynput import mouse

mouse_controller = mouse.Controller()

last_mouse_interaction_time = 0
last_right_click_time = 0


def on_move(x, y):
    utilities.mouse_position[0] += x
    utilities.mouse_position[1] += y
    if [x, y] != [0, 0]:
        mouse_controller.position = (0, 0)


def on_click(x, y, button, pressed):
    global last_mouse_interaction_time
    global last_right_click_time
    global current_palette_index

    current_time = time.time()
    last_mouse_interaction_time = current_time

    if pressed:
        if button == mouse.Button.left:
            utilities.mouse_clicks.append(button)
        elif button == mouse.Button.right:
            time_since_last_right_click = current_time - last_right_click_time
            if time_since_last_right_click < 0.3:
                current_palette_index = 0
            else:
                current_palette_index = (current_palette_index +
                                         1) % len(the_palettes)
            utilities.set_active_palette(the_palettes[current_palette_index])

            last_right_click_time = current_time


mouse_listener = mouse.Listener(on_move=on_move,
                                on_click=on_click,
                                suppress=True)
mouse_listener.start()

asyncio.run(main())
