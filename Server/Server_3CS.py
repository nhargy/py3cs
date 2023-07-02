import json
import argparse
import devserve
from devserve.servers import DeviceServer
from devserve.devices import device_directory
import time
from multiprocessing import Process
cfgs = []
import os

if __name__ == '__main__':
    print(devserve.__file__)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    #cfg_path = os.path.join(dir_path, "dev_config.json")
    filename = "dev_config.json"
    filename = os.path.join(dir_path, filename)
    with open(filename, "r") as f:
        cfgs = json.load(f)

    servers = []
    host = 'localhost'

    for i, cfg in enumerate(cfgs):
        port = 5000+i
        try:
            device = device_directory[cfg["device"]](**cfg)
            server = DeviceServer(cfg["name"], host, port, device)
            p = Process(target=server.run)
            print(f"starting device server for {cfg['name']}...")
            p.daemon = True
            p.start()
            servers.append(p)
            if p.is_alive():
                print(f"  OK   device server started. running on: {host}:{port}")

        except:
            print(f"  !!!FAIL!!! device server for {cfg['name']}...")
            pass

    try:
        while True:
            time.sleep(0.5)
    finally:
        for p in servers:
            p.terminate()
