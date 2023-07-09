# Author: Yentl Hendrickx
# Last modified: 2023-07-09
# Description: API handler, sends device info to API, gathers effect info

import requests
import socket
# import fcntl
import struct
from decouple import config

from storage.storage_handler import StorageHandler

# LED constants
DEVICE_NAME = config('DEVICE_NAME')
LED_COUNT = config('LED_COUNT')

# API constants
API_URL = config('API_URL')
API_PORT = config('API_PORT')
API_PING_ENDPOINT = config('API_PING_ENDPOINT')
API_INFO_ENDPOINT = config('API_INFO_ENDPOINT')


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return '192.168.199.250'
    # return socket.inet_ntoa(fcntl.ioctl(
    # s.fileno(),
    # 0x8915,
    # struct.pack('256s', ifname[:15].encode('utf-8')))[20:24])


def get_mac_address():
    try:
        mac_address = open('/sys/class/net/wlan0/address').readline()
    except:
        mac_address = "00:00:00:00:00:00"
    return mac_address.strip()


def get_data():
    ip = get_ip_address('wlan0')
    mac_address = get_mac_address()

    # Data to send to API
    return ({
        "name": DEVICE_NAME,
        "ip_address": ip,
        "mac_address": 'b8:27:eb:ce:f5:f4',
        # "mac_address": mac_address,
        "led_count": LED_COUNT,
    })

def send_device_info():
    # Get device data and send to api
    data = get_data()

    response = requests.get(
        f"{API_URL}:{API_PORT}{API_PING_ENDPOINT}", json=data)

    # check if response is ok
    if response.status_code == 200:
        device_id = response.json()['device_id']
        print(device_id)
        # Save device id to file

        store = StorageHandler('./storage.json')
        store.add_value({"device_id": device_id})
        return device_id
    
    return None


def get_effect_info():
    # get the effect information for this device
    store = StorageHandler('./storage.json')
    device_id = store.get_value('device_id')

    if device_id is None:
        device_id = send_device_info()

        if device_id == None:
            # No device id?
            exit(1)

    # DEBUG
    device_id = 1
         
    response = requests.get(
        f"{API_URL}:{API_PORT}{API_INFO_ENDPOINT}/{device_id}")

    # check if response is ok
    if response.status_code == 200:
        effect_info = response.json()
        return effect_info
    else:
        return None

