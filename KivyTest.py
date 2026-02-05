# Imports the kivy module
import kivy

# From kivy import the classes that will be used in the program
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel

# Import async and threading modules
import asyncio
import threading

# Imports bluetooth module
import socket

# Imports inverse kinematics modules and matplot
import ikpy.chain
import ikpy.utils.plot as plot_utils
import ipywidgets
import matplotlib.pyplot as plt

import numpy as np
import time
import math
from TestIK import plot, IK

# Import functions from other python files
from ControllerSupport import XboxController
from VoiceRecognition import recognize_speech_from_mic

# Ensures correct version of kivy is used
kivy.require('2.3.1')


position = [0,0,0]
orientation = [0,0,0]

chain = ikpy.chain.Chain.from_urdf_file("robot.urdf", active_links_mask=[False, True, True, True, True, True])

sVal =
sVal = [90,90,90,90,90,90]


def toggle_claw():
    print("toggle")

def move_x(direction):
    print("mx")

def move_y(direction):
    print("my")

def move_z(direction):
    print("mz")

def rotate_x(direction):
    print("rx")

def rotate_y(direction):
    print("ry")

def rotate_z(direction):
    print("rz")

# Function that repeats every second to update the servos
async def update_servo(bt_socket):
    # Creates temporary list to compare previous servo values with current
    temp = [90, 90, 90, 90, 90, 90]
    # Loops endlessly until the program ends
    while True:
        
        # Creates list to be used for the temporary
        s = []
        # Number indexed used to define the index in the list and to select the servo No in Arduino Code
        num = 1
        # Loops through Values and gets the values adding them to the next temp list
        for x in sVal:
            a = x
            s.append(a)
            # Comparing current values with previous and if they are different sends a command
            if a != temp[num - 1]:
                cmd = str(num) + " " + str(a)
                print(cmd)

                if bt_socket:
                    try:
                        bt_socket.send(cmd.encode())
                    except Exception as e:
                        print(f"Bluetooth send error: {e}")

            num += 1
        temp = s
        await asyncio.sleep(1)

async def update_controller(joystick):
    toggled = False
    while True:
        # Detects inputs and assigns it as variables
        b, lx, ly, rx, ry, lb, rb = joystick.read()



        if b ==0:
            toggled = False
        #toggles claw
        elif b ==1 and not toggled :
            toggled = True
            toggle_claw()

        # Dead zone region only calls function after certain value
        dead_value = 0.2

        # Move x, y and z
        if abs(lx)>=1-dead_value and lb !=0:
            move_z(lx)
        elif abs(lx)>=1-dead_value:
            move_x(lx)
        elif abs(ly)>=1-dead_value:
            move_y(ly)


        # Rotate x,y and z

        if abs(rx) >= 1 - dead_value and lb != 0:
            rotate_z(rx)
        elif abs(rx) >= 1 - dead_value:
            rotate_x(rx)
        elif abs(ry) >= 1 - dead_value:
            rotate_y(ry)


        await asyncio.sleep(0.01)

def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


# Creates a class to store the info of the .kv file
class MainWidget(TabbedPanel):
    def set_slider(self, idq):
        sVal[0] = int(self.ids.s1.value)
        sVal[1] = int(self.ids.s2.value)
        sVal[2] = int(self.ids.s3.value)
        sVal[3] = int(self.ids.s4.value)
        sVal[4] = int(self.ids.s5.value)
        sVal[5] = int(self.ids.s6.value)



# Main class that runs the app inheriting the class app from kivy module
class Controller(App):
    def build(self):
        # returns the main widget as the root widget
        return MainWidget()


if __name__ == "__main__":

    HC06_ADDRESS = "00:22:11:00:04:B8"
    PORT = 1  # Standard port for Bluetooth SPP

    # Try to create a Bluetooth socket
    bt_socket = None
    try:
        #bt_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        #bt_socket.connect((HC06_ADDRESS, PORT))
        print("Bluetooth connected successfully")
    except Exception as e:
        print(f"Bluetooth connection failed: {e}")
        print("Running in demo mode without Bluetooth")
        bt_socket = None

    joystick = XboxController()

    # Creates asyncio event loop
    loop1 = asyncio.new_event_loop()
    asyncio.run_coroutine_threadsafe(update_servo(bt_socket), loop1)
    asyncio.run_coroutine_threadsafe(update_controller(joystick), loop1)

    # Runs this loop in a separate thread
    threading.Thread(target=start_loop, args=(loop1,), daemon=True).start()



    # The app is initialized at runtime
    # And its run method is called
    Controller().run()

