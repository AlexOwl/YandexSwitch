import tradetuya
import socket
import time

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

        self.connection = None
        self.listeners = []
        self.tasks = []

        self._start_tasks()
        
    def _start_tasks(self):
        for target in [self._daemon_heart_beat, self._daemon_receive_data]:
            self.tasks.append(helper.create_task(target))

    @property
    def _device(self):
        return {
            "ip": self.ip,
            "deviceid": self.deviceid,
            "localkey": self.localkey,
            "protocol": "3.3"
        }

    def connect(self):
        self._fire_event({ "dps": helper.generate_get_control(self.schema) })
        self._fire_event({ "dps": { self.switch_id: False } })
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
            self.connection = None

        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        # self.connection.settimeout(TCP_TIMEOUT)

        try:
            self.connection.connect((self.ip, TCP_PORT))
            self.get_control()
        except:
            time.sleep(3)
            self.connect()

    def _fire_event(self, reply):
        data = helper.proccess_reply(reply)

        for listener in self.listeners:
            listener(data)

    def _daemon_heart_beat(self):
        while True:
            time.sleep(HEART_BEAT_PERIOD)
            self.send_request(tradetuya.HEART_BEAT)

    def _daemon_receive_data(self):
        while True:
            data = None

            try: 
                data = self.connection.recv(4096)
            except:
                pass

            if not data:
                self.connect()
                continue
                
            try:
                for reply in tradetuya._process_raw_reply(self._device, data):
                    self._fire_event(reply)
            except:
                pass

    def set_control(self, data): 
        data = helper.generate_set_control(self.schema, data)
        print(data)
        for request in helper.chunks_dict(data, 5):
            self.send_request(tradetuya.CONTROL_NEW, request)

    def get_control(self):
        data = helper.generate_get_control(self.schema)
        for request in helper.chunks_dict(data, 10):
            self.send_request(tradetuya.CONTROL_NEW, request)

    def send_request(self, command, payload = None):
        try:
            request = tradetuya._generate_payload(self._device, 0, command, payload)
            self.connection.send(request)
        except:
            self.connect()
