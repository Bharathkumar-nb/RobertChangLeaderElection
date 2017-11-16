import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import Tkinter as tk
import signal

class OneLeader(object):
    """docstring for Fork"""
    def __init__(self):
        self.leader = False
        self.working = False
        self.traces = []

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

        # Tkinter initialization
        self.root = tk.Tk()
        self.status = tk.Label(self.root, text="Have leader before working\n\n", justify="left")
        self.status.grid()
        self.root.minsize(400, 400)
        self.root.mainloop()

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
        self.traces.append(msg)
        tokens = msg.payload.split('.')
        msg, _ = tokens
        if msg == 'log_i_am_leader':
            self.leader = True
        if msg == 'log_do_real_work':
            if not self.leader:
                self.root.after(500, self.gui_update())
                print("Assert")

    def gui_update(self):
        self.current_status = self.status["text"]
        self.current_status += 'ERROR: Violation of LTL property\n'
        self.current_status += 'Traces for error\n'
        isFirstIteration = True
        for trace in self.traces:
            if not isFirstIteration:
                self.current_status +=  " -> "
            else:
                isFirstIteration = False
                self.current_status +=  "      "
            self.current_status +=  trace + '\n'
        self.current_status += '\n\n'
        self.status["text"] = self.current_status

def main():

    OneLeader()
    
    while True:
        time.sleep(10)

main()