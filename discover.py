import yaml
import asyncio

import kasa
from pywizlight import discovery

async def discover_kasa():
    devices = await kasa.Discover.discover(target='192.168.11.255')
    dimmers = {}
    for ip, dev in devices.items():
        dimmers[dev.alias] = ip

    print(yaml.dump(dimmers, default_flow_style=False), end='')

    with open('dimmers.yml', 'w') as f:
        yaml.dump(dimmers, f, default_flow_style=False)

async def discover_wiz():
    with open("macs.yml", "r") as file:
        macs = yaml.safe_load(file)

    bulbs = await discovery.discover_lights(broadcast_space="192.168.11.255", wait_time=20)

    print(len(bulbs))
    print(yaml.dump([(bulb.ip, bulb.mac) for bulb in bulbs]))

    ips = []
    for mac in macs:
        print(mac)
        ips.append(next(bulb.ip for bulb in bulbs if bulb.mac == mac))

    with open('ips.yml', 'w') as file:
        yaml.dump(ips, file, default_flow_style=False)


async def main():
    await discover_kasa()
    await discover_wiz()

asyncio.run(main())
