# Imports the kivy module
import kivy

# From kivy import the classes that will be used in the program
from kivy.app import App

from kivy.uix.tabbedpanel import TabbedPanel

import asyncio
import threading
import socket

from TestIK import plot
from ControllerSupport import XboxController

# Ensures correct version of kivy is used
kivy.require('2.3.1')

sVal = [90, 90, 90, 90, 90, 90]

def toggle_claw():
    pass

def move_x(direction):
    pass

def move_y(direction):
    pass

def move_z(direction):
    pass

def rotate_x(direction):
    pass

def rotate_y(direction):
    pass

def rotate_z(direction):
    pass

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
    while True:
        input=joystick.read()
        if input[0] != 1:
            toggle_claw()

        if input[1] != 0:
            move_x(input[1])
        if input[2] != 0:
            move_y(input[1])
        if input[1] != 0 and input[5] !=0:
            move_z(input[1])
        if input[1] != 0:
            move_x(input[1])

        await asyncio.sleep(0.5)

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

