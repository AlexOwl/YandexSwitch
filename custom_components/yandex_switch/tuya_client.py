import tradetuya
import socket
import time
import asyncio

try:
    from . import helper
except:
    import helper

TCP_PORT = 6668
TCP_TIMEOUT = 30
HEART_BEAT_PERIOD = 10

class TuyaClient:
    def __init__(self, ip, deviceid, localkey, schema, switch_id=None):
        self.ip = ip
        self.deviceid = deviceid
        self.localkey = localkey
        self.schema = schema
        self.switch_id = switch_id or helper.find_switch_dp(schema) or "1"

        self.listeners = []

    @property
    def _device(self):
        return {
            "ip": self.ip,
            "deviceid": self.deviceid,
            "localkey": self.localkey,
            "protocol": "3.3"
        }

    async def run_forever(self, loop=None):
        self._loop = loop

        self.socket_lock = asyncio.Event(loop=self._loop)

        asyncio.create_task(self.socket_establish_connection())
        asyncio.create_task(self.socket_heart_beat())

    async def socket_establish_connection(self):
        while True:
            print("reconnect")
            try:
                self.socket_reader, self.socket_writer = await asyncio.wait_for(asyncio.open_connection(self.ip, TCP_PORT, loop=self._loop), TCP_TIMEOUT, loop=self._loop)
                await self.on_connected()

                while True:
                    data = await self.socket_reader.read(4096)
                    if not data:
                        raise Exception()
                    asyncio.create_task(self.proccess_data(data))
            except:
                await self.on_disconnected()
                await asyncio.sleep(10, loop=self._loop)

    async def on_connected(self): 
        print("on connected")
        self.socket_lock.set()

        await self.send_control_request()

    async def on_disconnected(self):
        print("on disconnect")
        self.socket_lock.clear()

        reply = { "dps": helper.generate_get_control(self.schema) }
        #reply["dps"][self.switch_id] = False
        await self.fire_event(reply)

    async def fire_event(self, data):
        for listener in self.listeners:
            asyncio.create_task(listener(data))

    async def proccess_data(self, data):
        for reply_str in tradetuya._process_raw_reply(self._device, data):
            await self.fire_event(helper.proccess_reply(reply_str))

    async def socket_heart_beat(self):
        while True:
            await asyncio.sleep(HEART_BEAT_PERIOD)
            if self.socket_lock.is_set():
                asyncio.create_task(self.send_request(tradetuya.HEART_BEAT))

    async def send_control_request(self, data = None):
        data =  helper.generate_get_control(self.schema) if not data else helper.generate_set_control(self.schema, data)
        for request in helper.chunks_dict(data, 10):
            asyncio.create_task(self.send_request(tradetuya.CONTROL_NEW, request))

    async def send_request(self, command, payload = None):
        request = tradetuya._generate_payload(self._device, 0, command, payload)
        await self.socket_write(request)

    async def socket_write(self, message):
        await self.socket_lock.wait()
        self.socket_writer.write(message)
