import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal
import mraa

# Init LEDs
leds = []
for i in range(2,10):
    led = mraa.Gpio(i)
    leds.append(led)

# Constants
CONTENTION = 0
BOWOUT = 2
LEADER = 4

class CheaterNode(object):
    """docstring for Fork"""
    def __init__(self, _id, nid, initiator):
        self._id = str(_id)
        self.nid = str(nid)
        self.initiator = (str(initiator) == '1')
        self.done = False

        signal.signal(signal.SIGINT, self.control_c_handler)

        # MQTT initialization
        self.mqtt_client = paho.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_log = self.on_log
        self.mqtt_topic = 'kappa/node'
        self.mqtt_client.will_set(self.mqtt_topic, '_____Will of '+self._id+' ____\n\n', 0, False)
        self.mqtt_client.connect('sansa.cs.uoregon.edu', '1883', keepalive=300)
        self.mqtt_client.subscribe('kappa/node')
        self.mqtt_client.loop_start()

        self.turnOnLED(CONTENTION)

        if self.initiator:
            print('send_id.'+self.nid+"."+self._id)
            self.mqtt_client.publish(self.mqtt_topic, 'send_id.'+self.nid+"."+self._id)
            self.turnOffLED(CONTENTION)
            print('send_leader.'+self.nid+"."+self._id)
            self.mqtt_client.publish(self.mqtt_topic, 'send_leader.'+self.nid+"."+self._id)
            print ('log_do_real_work.'+self._id+'.'+self._id)
            self.mqtt_client.publish(self.mqtt_topic, 'log_do_real_work.'+self._id+'.'+self._id)
            self.done = True

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
        if len(tokens) == 3:
            msg,rid,payload = tokens
            if rid == self._id:
                if msg =='send_id' and not self.done:
                    print('send_id.'+self.nid+"."+self._id)
                    self.mqtt_client.publish(self.mqtt_topic, 'send_id.'+self.nid+"."+self._id)
                    print('log_i_am_leader.'+self._id)
                    self.mqtt_client.publish(self.mqtt_topic, 'log_i_am_leader.'+self._id)
                    self.turnOffLED(CONTENTION)
                    self.turnOnLED(LEADER)
                    print('send_leader.'+self.nid+"."+self._id)
                    self.mqtt_client.publish(self.mqtt_topic, 'send_leader.'+self.nid+"."+self._id)
                    print ('log_do_real_work.'+self._id+'.'+self._id)
                    self.mqtt_client.publish(self.mqtt_topic, 'log_do_real_work.'+self._id+'.'+self._id)
                    self.done = True

    # LED functions
    def turnOnLED(self, led_no):
        leds[led_no].write(0)

    def turnOffLED(self, led_no):
        leds[led_no].write(1)


def main():
    arr = sys.argv
    if  len (arr) != 4 :
        print ('Please enter valid input, e.g. python Node.py <id> <nid> <[0,1] initiator>')
        sys.exit(1)
    if arr[3] not in '01':
        print ('Please enter valid number 0 or 1')
        sys.exit(1)

    CheaterNode(arr[1],arr[2],arr[3])
    
    while True:
        time.sleep(10)

main()