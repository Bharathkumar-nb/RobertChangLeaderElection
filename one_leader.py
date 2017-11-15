import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal

class OneLeader(object):
    """docstring for Fork"""
    def __init__(self):
        self.currentLeader = None

        signal.signal(signal.SIGINT, self.control_c_handler)

        # MQTT initialization
        self.mqtt_client = paho.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_log = self.on_log
        self.mqtt_topic = 'kappa/one_leader'
        self.mqtt_client.will_set(self.mqtt_topic, '_____Will of '+self._id+' ____\n\n', 0, False)
        self.mqtt_client.connect('sansa.cs.uoregon.edu', '1883', keepalive=300)
        self.mqtt_client.subscribe('kappa/node')
        self.mqtt_client.loop_start()


    # Deal with control-c
    def control_c_handler(self, signum, frame):
        self.isDisconnected = True
        self.mqtt_client.disconnect()
        self.mqtt_client.loop_stop()  # waits until DISCONNECT message is sent out
        print ("Exit")
        sys.exit(0)

    # MQTT Handlers
    def on_connect(self, client, userdata, flags, rc):
        pass

    def on_disconnect(self, client, userdata, rc):
        pass

    def on_log(self, client, userdata, level, buf):
        pass

    def on_message(self, client, userdata, msg):
        tokens = msg.payload.split('.')
        if len(tokens) == 2:
            msg, _id = tokens
            if msg == 'log_i_am_leader':
                if not self.currentLeader:
                    self.currentLeader = _id
                elif _id != self.currentLeader:
                    print('Assert')

def main():

    OneLeader()
    
    while True:
        time.sleep(10)

main()