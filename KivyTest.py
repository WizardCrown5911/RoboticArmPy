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
import TestIK

# Import functions from other python files
from ControllerSupport import XboxController
from VoiceRecognition import recognize_speech_from_mic

# Ensures correct version of kivy is used
kivy.require('2.3.1')

velocity = [0.0] * 6  # [vx, vy, vz, wx, wy, wz]
  # x, y, z

sVal = [90,90,90,90,90,100]



xymax = 2.3
zmax = 3

def apply_deadzone(x, dz=0.2):
    if abs(x) < dz:
        return 0.0
    if x > 0:
        return (x - dz) / (1 - dz)
    else:
        return (x + dz) / (1 - dz)


def toggle_claw(toggled ):

    if toggled:
        sVal[5] = 0
        return False
    else:
        sVal[5] = 100
        return True



# Function that repeats every second to update the servos
async def update_servo(bt_socket):
    global velocity

    temp = ""

    while True:
        dt = 0.01

        # Update joints using velocity IK
        joints = TestIK.update_joints_from_velocity(np.array(velocity), dt)

        # Convert to servo angles
        angles = TestIK.get_servo_angles()
        angles.append(sVal[5])  # claw

        cmd= ""

        for x in angles:
            cmd += str(x) +","
        cmd = cmd[:-1] + "\n"


        if cmd != temp:
            temp = cmd
            try:
                print(cmd)
                if bt_socket:
                    bt_socket.send(cmd.encode())
                await asyncio.sleep(0.02)
            except Exception as e:
                print(f"Bluetooth send error: {e}")

        await asyncio.sleep(dt)

import TestIK  # ADD THIS

async def update_controller(joystick):
    global velocity

    movement_mode = True
    speed_mode = False

    prev_rb = 0
    prev_lb = 0

    toggle = False
    claw = True

    rb_pressed = False
    lb_pressed = False

    while True:
        b, lx, ly, rx, ry, lb, rb = joystick.read()

        lx = apply_deadzone(lx)
        ly = apply_deadzone(ly)
        rx = apply_deadzone(rx)
        ry = apply_deadzone(ry)

        # ---- CLAW ----
        if b == 0:
            toggle = False
        elif b == 1 and not toggle:
            toggle = True
            claw = toggle_claw(claw)


        # ---- RB TOGGLE (movement mode) ----
        if rb == 1 and not rb_pressed:
            movement_mode = not movement_mode
            print(f"Movement mode: {movement_mode}")
            rb_pressed = True

        if rb == 0:
            rb_pressed = False

        # ---- LB TOGGLE (speed mode) ----
        if lb == 1 and not lb_pressed:
            speed_mode = not speed_mode
            print(f"Speed mode: {speed_mode}")
            lb_pressed = True

        if lb == 0:
            lb_pressed = False

        # ---- SPEED ----
        if speed_mode:
            pos_speed = 1.0
            rot_speed = 0.04
        else:
            pos_speed = 0.3
            rot_speed = 0.02

        if movement_mode:
            yaw = TestIK.get_base_yaw()


            # Rotation matrix (2D)
            cos_y = np.cos(yaw)
            sin_y = np.sin(yaw)

            # Controller input
            forward = lx  # forward/back
            strafe = -ly  # left/right

            # Rotate into world frame
            vx = pos_speed * (forward * cos_y - strafe * sin_y)
            vy = pos_speed * (forward * sin_y + strafe * cos_y)
            vz = pos_speed * ry  # up/down

            velocity = [vx, vy, vz, 0, 0, 0]


        else:
            # Manual rotation
            TestIK.adjust_joint(1, rot_speed * lx)  # base
            TestIK.adjust_joint(4, rot_speed * rx)  # wrist
            TestIK.adjust_joint(5, rot_speed * ry)  # wrist

            velocity = [0, 0, 0, 0, 0, 0]

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
        bt_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        bt_socket.connect((HC06_ADDRESS, PORT,))
        print("Bluetooth connected successfully")
    except Exception as e:
        print(f"Bluetooth connection failed: {e}")
        print("Running in demo mode without Bluetooth")
        bt_socket = None

    
    joystick = XboxController()

    chain = ikpy.chain.Chain.from_urdf_file("robot.urdf", active_links_mask=[False, True, True, True, True, True])

    # Creates asyncio event loop
    loop1 = asyncio.new_event_loop()
    asyncio.run_coroutine_threadsafe(update_servo(bt_socket), loop1)
    asyncio.run_coroutine_threadsafe(update_controller(joystick), loop1)

    # Runs this loop in a separate thread
    threading.Thread(target=start_loop, args=(loop1,), daemon=True).start()



    # The app is initialized at runtime
    # And its run method is called
    Controller().run()

