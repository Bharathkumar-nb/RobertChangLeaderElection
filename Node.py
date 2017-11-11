import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal

class Node(object):
    """docstring for Fork"""
    def __init__(self, _id, nid, initiator):
        self._id = str(_id)
        self.nid = str(nid)
        initiator = str(initiator)
        self.initiator = (initiator == '1')

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

        self.main = self.initiator
        self.bowout = False
        self.working = False
        self.waitforroundtrip = False
        

        if self.initiator:
            print('send_id.'+self.nid+"."+self._id)
            self.mqtt_client.publish(self.mqtt_topic, 'send_id.'+self.nid+"."+self._id)
            self.main = False

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
        #print(msg.payload)
        # send_id.nid.k, send_leader.nid.k
        msg,rid,payload = msg.payload.split('.')
        if rid == self._id:
            if not self.bowout:
                if msg =='send_id':
                    print('log_deciding.'+self._id+'.'+payload)
                    if payload<self._id:
                        print ('log_drop.'+self._id+'.'+payload)
                        if not self.initiator:
                            print('send_id.'+self.nid+"."+self._id)
                            self.mqtt_client.publish(self.mqtt_topic, 'send_id.'+self.nid+"."+self._id)
                    elif payload>self._id:
                        print('send_id.'+self.nid+"."+payload)
                        self.mqtt_client.publish(self.mqtt_topic, 'send_id.'+self.nid+"."+payload)
                        self.bowout = True
                    else: 
                        print('log_i_am_leader.'+self._id)
                        print('send_leader.'+self.nid+"."+self._id)
                        self.mqtt_client.publish(self.mqtt_topic, 'send_leader.'+self.nid+"."+self._id)
                        self.waitforroundtrip = True
                if msg =='send_leader':
                    if not self.waitforroundtrip:
                        self.mqtt_client.publish(self.mqtt_topic, 'send_leader.'+self.nid+"."+payload)
                        self.working = True
                    else:
                        print ('log_all_informed.'+self._id)
                    print ('log_do_real_work.'+self._id+'.'+payload)
                    print ('log_waiting')
                        
            else :
                if msg =='send_id':
                    print('send_id.'+self.nid+"."+payload)
                    self.mqtt_client.publish(self.mqtt_topic,'send_id.'+self.nid+"."+payload)
                if msg == 'send_leader' :
                    if not self.working:
                        print('send_leader.'+self.nid+"."+payload)
                        self.mqtt_client.publish(self.mqtt_topic, 'send_leader.'+self.nid+"."+payload)
                        self.working = True
                        print ('log_do_real_work.'+self._id+'.'+payload)
                        print ('log_waiting')

    # LED functions
    def turnOnLED(self):
        leds[self.led_no].write(0)

    def turnOffLED(self):
        leds[self.led_no].write(1)


def main():
    arr = sys.argv
    if  len (arr) != 4 :
        print ('Please enter valid input, e.g. python Node.py <id> <nid> <[0,1] initiator>')
        sys.exit(1)
    if arr[3] not in '01':
        print ('Please enter valid number 0 or 1')
        sys.exit(1)

    Node(0,1,0)
    Node(2,0,0)
    Node(1,2,1)
    
    while True:
        time.sleep(10)

main()