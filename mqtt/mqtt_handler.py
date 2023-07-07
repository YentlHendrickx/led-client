# Author: Yentl Hendrickx
# Last modified: 2023-07-07
# Description: MQTT handler class

import paho.mqtt.client as mqtt

class MQTTHandler:
    def __init__(self, broker, port, topic):
        self.broker = broker
        self.port = port
        self.topic = topic

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print('Connected to broker')
            client.subscribe(self.topic)
        else:
            print('Connection failed!')

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        print('Received message: ' + payload) 
    
    def start(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        client.connect(self.broker, self.port, 60)
        client.loop_forever()

        