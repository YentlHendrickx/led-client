import requests
import socket
import fcntl
import struct
from decouple import config

# LED
DEVICE_NAME = config('DEVICE_NAME')
LED_COUNT = config('LED_COUNT')

# API
API_URL = config('API_URL')
API_PORT = config('API_PORT')
API_PING_ENDPOINT = config('API_PING_ENDPOINT')
API_INFO_ENDPOINT = config('API_INFO_ENDPOINT')


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,
        struct.pack('256s', ifname[:15].encode('utf-8')))[20:24])


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
        "mac_address": mac_address,
        "led_count": LED_COUNT,
    })


def send_device_info():
    # Get device data and send to api
    data = get_data()

    response = requests.get(
        f"${API_URL}:{API_PORT}{API_INFO_ENDPOINT}", json=data)

    # Save device id to file
    device_id = response.json()["device_id"]
    with open("../device_id.config", "w") as f:
        f.write(device_id)
