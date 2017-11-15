import Tkinter as tk

import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal

class Assert(object):
    """docstring for Fluents"""

    def __init__(self, expr1, expr2):
        self.MY_NAME = 'Asserts'

        self.expr1 = expr1
        self.expr2 = expr2
        self.isExpr1 = False
        self.isExpr2 = False
        self.traces = []
       
        # Handle Ctrl+C
        signal.signal(signal.SIGINT, self.control_c_handler)

        # MQTT initialization
        self.mqtt_client = paho.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_log = self.on_log
        self.mqtt_topic = 'kappa/asserts'
        self.mqtt_client.will_set(self.mqtt_topic, '______________Will of '+self.MY_NAME+' _________________\n\n', 0, False)
        self.mqtt_client.connect('sansa.cs.uoregon.edu', '1883')
        self.mqtt_client.subscribe('kappa/node', 0)
        self.mqtt_client.loop_start()
         #Tkinter initialization
        self.root = tk.Tk()
        self.status = tk.Label(self.root, text="Weak Until\n\n", justify="left")
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

    # MQTT Handlers
    def on_connect(self, client, userdata, flags, rc):
        pass

    def on_disconnect(self, client, userdata, rc):
        pass

    def on_log(self, client, userdata, level, buf):
        pass

    # Fluents functions
    def on_message(self, client, userdata, msg):
        mapped_msg = msg.payload
        if mapped_msg != '':
            self.traces.append(mapped_msg)

        if(mapped_msg == self.expr1) :
            if self.isExpr2:
                self.expr1 = True
            else:
                print(self.traces)
                self.root.after(1000, self.gui_update())
                print("Assert1")
        elif(mapped_msg == self.expr2):
            if not self.expr1:
                self.isExpr2 = True
            else:

                print(self.traces)
                self.root.after(1000, self.gui_update())
                print("Assert2")

def main():
    arr = sys.argv
    if  len (arr) != 3 :
        print ('Please enter valid input, e.g. python weak_until.py <expr1> <expr2>')
        sys.exit(1)
    
    Assert(arr[1], arr[2])
    while True:
        time.sleep(10)

main()