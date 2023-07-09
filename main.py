# Author: Yentl Hendrickx
# Last modified: 2023-07-09
# Description: Main file, starts MQTT and effects processes


# Import handlers
from mqtt.mqtt_handler import MQTTHandler
from api.api_handler import send_device_info, get_effect_info
from effects.led_effects import start_effects

# Import other modules
from decouple import config
from threading import Thread
import multiprocessing
from enum import Enum
import signal
import sys
import os

# Get constants from .env file
MQTT_BROKER = config("MQTT_BROKER")
MQTT_PORT = int(config("MQTT_PORT"))
MQTT_TOPIC = config("MQTT_TOPIC")

# Enum to define MQTT payloads
class Payloads(Enum):
    UPDATE = 'update'
    GET_INFO = 'get_info'

# Handle MQTT payload and call API functions
def handle_mqtt_payload(payload, queue):
    data = None
    print(f"Received message {payload}")

    # Identify payload and respond accordingly
    if payload == Payloads.UPDATE.value:
        data = get_effect_info()
    elif payload == Payloads.GET_INFO.value:
        send_device_info()
    else:
        print(f"Unknown payload: {payload}")
    
    # If data was returned, append it to the queue
    if data is not None:
        queue.put(data)

def main():
    # Termination events to trigger shutdown 
    termination_event = multiprocessing.Event()
    effects_termination_event = multiprocessing.Event()
    # Effects queue to pass data to effects process
    effects_queue = multiprocessing.Queue()
    # Effects process using the queue and termination event
    effects_process = multiprocessing.Process(target=start_effects, args=(effects_queue, effects_termination_event))
    # start the effects process
    effects_process.start()
    mqtt_handler = None

    # Signal handler for SIGINT (shutdown)
    def signal_handler(signal, frame): 
        print("Terminating...")

        # Termination triggered
        termination_event.set()

    # Register SIGINT handler
    signal.signal(signal.SIGINT, signal_handler)

    # Start MQTT handler, payload using lambda to pass args
    mqtt_handler = MQTTHandler(MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, lambda payload: handle_mqtt_payload(payload, effects_queue))

    def mqtt_start_handler():
        mqtt_handler.start()

    # Start MQTT handler in separate thread
    mqtt_thread = Thread(target=mqtt_start_handler)
    mqtt_thread.start()

    # Main loop, wait for termination event
    while True:
        if termination_event.is_set():
            # Stop MQTT handler
            if mqtt_handler:
                mqtt_handler.stop()

            # Stop effects process
            if effects_process:
                # Try os kill, set termination event and wait for destruction
                os.kill(effects_process.pid, signal.SIGINT)
                effects_termination_event.set()
                effects_process.join()

            sys.exit(0)

if __name__ == "__main__":
    main()
