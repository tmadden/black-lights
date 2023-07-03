import asyncio
import json
import logging
import socket
import time
import asyncio_dgram

from pywizlight.rgbcw import hs2rgbcw, rgb2rgbcw, rgbcw2hs
from pywizlight import PilotBuilder

_LOGGER = logging.getLogger(__name__)


class Light:

    def __init__(self, ip, port=38899):
        self.ip = ip
        self.port = port
        self.state = None
        self.next_message_id = 1
        self.id_of_last_change = 0
        self.id_to_look_for = 0
        self.in_sync = False
        self.staleness = 0
        self.staleness_threshold = 1000

    async def connect(self):
        self.stream = await asyncio_dgram.connect((self.ip, self.port))

    def generate_update_message(self):
        if self.state:
            # if not self.previous_state:
            params = self.state
            if 'brightness' not in params:
                params['brightness'] = 255
            params['state'] = True
            return json.dumps({
                'method': 'setPilot',
                'id': self.next_message_id,
                'params': params
            })
            # else:
            #     message = PilotBuilder(rgb=(255, 255, 255),
            #                         brightness=self.state).set_state_message(
            #                             self.next_message_id)
        else:
            message = json.dumps({
                'method': 'setPilot',
                'id': self.next_message_id,
                'params': {
                    'state': False
                }
            })
        self.next_message_id += 1
        return message

    async def send_update(self):
        if self.staleness >= self.staleness_threshold:
            await self.stream.send(
                bytes(self.generate_update_message(), "utf-8"))
            self.staleness_threshold *= 2
            self.staleness = 0
        if not self.in_sync:
            await self.stream.send(
                bytes(self.generate_update_message(), "utf-8"))
            self.staleness = 0
        else:
            self.staleness += 1

    async def comm_loop(self):
        next_frame_time = time.perf_counter()

        while True:
            next_frame_time += 0.05
            now = time.perf_counter()
            try:
                data, remote_addr = await asyncio.wait_for(
                    self.stream.recv(), next_frame_time - now)
                response = json.loads(data.decode())
                if 'result' in response and 'success' in response[
                        'result'] and response['result'][
                            'success'] and 'id' in response:
                    if response['id'] >= self.id_to_look_for:
                        self.in_sync = True
                    elif response['id'] < self.id_of_last_change:
                        self.id_to_look_for = self.next_message_id
                        self.in_sync = False
            except asyncio.TimeoutError:
                pass
            await self.send_update()

    def get_state(self):
        return self.state

    def set_state(self, state, seriously=False):
        if self.state != state:
            self.previous_state = self.state
            self.in_sync = False
            self.id_of_last_change = self.next_message_id
            self.id_to_look_for = self.next_message_id
            self.state = state
            self.staleness_threshold = 1 if seriously else 4
