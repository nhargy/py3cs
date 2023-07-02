import requests
import ast
import json
from typing import Dict
import threading
import time
import socket
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict


NTRIES = 3
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
myip = s.getsockname()[0]
s.close()


class DeviceClient:
    def __init__(self, name, addr: str):
        self._name = name
        self._addr = addr

    def __getattr__(self, item):
        if item.startswith('_'):
            return super().__getattribute__(item)
        try:
            for _ in range(NTRIES):
                try:
                    resp = requests.get('{addr}/{item}'.format(addr=self._addr, item=item), timeout=30)
                    if resp.status_code is 200:
                        break

                    time.sleep(0.1)
                except:
                    pass
            if resp.status_code is 200:
                val = None
                try:
                    val = resp.json().get('value', None)
                except:
                    pass
                try:
                    val = ast.literal_eval(resp.json().get('value', None))
                except:
                    pass
                return val
        except:
            raise ConnectionError('Device address unavailable. Is the server running?')
        raise AttributeError('Attribute {} is not available'.format( item))

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super().__setattr__(key, value)
        else:
            try:
                resp = requests.put('{addr}/{key}'.format(addr=self._addr, key=key), data={"value": value}, timeout=300)
                if resp.status_code is 201:
                    val = None
                    try:
                        val = resp.json().get('value', None)
                    except:
                        pass
                    try:
                        val = ast.literal_eval(resp.json().get('value', None))
                    except:
                        pass
                    return val
                else:
                    val = getattr(self, key)
                    return val
                    # raise 'Bad response from server code: {}'.format(resp.status_code)
            except:
                raise ConnectionError('Device address unavailable. Is the server running?')

    def __dir__(self):
        return super().__dir__() + self.attributes

    def set_state(self, state: dict):
        attrs = self.attributes
        for attr in attrs:
            if attr in state:
                setattr(self, attr, state[attr])

    def get_state(self, attrs=None):
        if attrs is None:
            attrs = self.attributes
       
        state = {attr: getattr(self, attr) for attr in attrs}
        return state
    
class RecordingDeviceClient(DeviceClient):
    
    def __init__(self, name, addr: str):
        super().__init__(name, addr)
        self._record_mode = 'None'
        self.__recording = set()
        self._record_delay = 10

    @property
    def _recording(self):
        return self.__recording

    @_recording.setter
    def _recording(self, value):
        if value in self.attributes:
            self.__recording.add(value)
        if len(self.__recording)==1:
            self._thread = threading.Thread(target=self.recorder)
            self._thread.setDaemon(True)
            self._thread.start()

    @property
    def _stop_recording(self):
        return set(self.attributes).difference(self.__recording)

    @_stop_recording.setter
    def _stop_recording(self, value):
        if value in self.__recording:
            self.__recording.remove(value)

    def recorder(self):
        from influxdb import InfluxDBClient
        influx = InfluxDBClient(host='localhost', port=8086)
        dbs = influx.get_list_database()
        if "recordings" not in [d['name'] for d in dbs]:
            influx.create_database("recordings")
        while True:
            if not len(self.__recording):
                break
            for attr in self.__recording:
                if self._record_mode is 'influx':
                    data = {
                        "measurement": attr,
                        "fields":{
                            "name": attr,
                            "device": self._name,
                            "value": getattr(self, attr)
                        }
                    }
                    influx.write_points([data], database="recordings")

                elif self._record_mode is 'mongo':
                    pass

                elif self._record_mode is 'file':
                    pass
            time.sleep(self._record_delay)

ClientDict = Dict[str, DeviceClient]


# class GlobalStorage:
#     attributes = []
#     connected = True
#

class SystemClient:

    def __init__(self, devices: ClientDict):
        self.devices = devices
        # if "experiment" not in self.devices:
        #     self.devices['experiment'] = GlobalStorage()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def validate_device_connections(self):
        for device_name, device in self.devices.items():
            print(f"Checking {device_name}... ", end="", flush=True)
            try:
                if not device.connected:
                    # Try to reconnect again
                    device.port = device.port
                    time.sleep(0.5)
            except ConnectionError:
                print(f"Device {device_name} does not respond. Check the connection.")
                raise
            finally:
                print("OK" if device.connected else "FAIL")


    @classmethod
    def from_json_file(cls, host ,path: str):
        with open(path, "r") as f:
            cfgs = json.load(f)
        clients = {}
        for i, cfg in enumerate(cfgs):
            addr = f'http://{host}:{5000+i}/{cfg["name"]}'
            c = DeviceClient(name=cfg["name"],addr=addr)
            clients[cfg["name"]] = c
        return cls(clients)

    @classmethod
    def from_config_file(cls, path: str):
        import configparser
        config = configparser.ConfigParser()
        config.read(path)
        clients = {}
        for idx, name in enumerate(config.sections()):
            cfg = {k:v.format(idx=idx, myip=myip) for k,v in config[name].items()}
            addr = f'http://{cfg["host"]}:{cfg["port"]}/{name}'
            c = DeviceClient(name, addr)
            clients[name] = c
        return cls(clients)

    @classmethod
    def from_dict(cls, cfgs: str, host='localhost'):
        clients = {}
        for i, cfg in enumerate(cfgs):
            addr = f'http://{host}:{5000+i}/{cfg["name"]}'
            c = DeviceClient(cfg["name"], addr)
            clients[cfg["name"]] = c
        return cls(clients)

    def set_state_async(self, states: dict):
        ts = []
        for name, state in states.items():
            dev = self.devices.get(name)
            t = threading.Thread(target=dev.set_state, args=(state,)) 
            t.start()
            ts.append(t)
            time.sleep(0.05)
        for t in ts:
            t.join()

    def set_state(self, states: dict):
        for name, state in states.items():
            dev = self.devices.get(name)
            dev.set_state(state)
  

    def get_state(self, fetch=None):
        if fetch is None:
            fetch = {name: dev.attributes for name, dev in self.devices.items()}
        state = {}
        for name, attrs in fetch.items():
            device = self.devices[name]
            state[name] = device.get_state(attrs)
        return state

    def get_state_async(self, fetch=None):
        if fetch is None:
            fetch = {name: dev.attributes for name, dev in self.devices.items()}

        with ThreadPoolExecutor(10) as pool:
            futures_to_name = {}
            for name, attrs in fetch.items():
                device = self.devices[name]
                futures = {pool.submit(device.get_state, attrs): name}
                futures_to_name.update(futures)

            state = defaultdict(dict)
            for future in as_completed(futures_to_name):
                name = futures_to_name[future]
                try:
                    result = future.result()
                except Exception as exc:
                    self.logger.info(f'{name} generated an exception: {exc}')
                else:
                    state[name] = result
        return dict(state)

    def __getattr__(self, item):
        try:
            return self.devices.get(item)
        except:
            raise AttributeError('System has no device {}'.format(item))

    def __getitem__(self, key):
        return getattr(self, key)

    def __dir__(self):
        return super().__dir__() + list(self.devices.keys())
