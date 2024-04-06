# Author: Yentl Hendrickx
# Last modified: 2024-04-06
# Description: MQTT handler class

import paho.mqtt.client as mqtt
import threading
import time


class MQTTHandler:
    def __init__(self, broker, port, topic, payload_handler):
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self.topic = topic
        self.payload_handler = payload_handler
        self.termination_event = threading.Event()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print('Connected to broker')
            print(f"subscribing to {self.topic}")
            client.subscribe(self.topic)
        else:
            print('Connection failed!')

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        print(payload)
        self.payload_handler(payload)


    def start(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        print(self.broker, self.port)
        self.client.connect(self.broker, self.port, 60)

        while not self.termination_event.is_set():
            self.client.loop(0.1)

    def stop(self):
        self.termination_event.set()
        self.client.loop_stop()
        self.client.disconnect()
