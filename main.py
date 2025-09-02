import tkinter as tk
from tkinter import ttk

import socket

from PIL import ImageTk, Image

import os
import sys

import asyncio
import threading

import ikpy


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def loading_page():
    def close_loading():
        root.destroy()

    # creates a window called root and sets title and size as well as background colour
    root = tk.Tk()
    root.title("Loading Page")
    root.geometry("600x500")
    root.configure(bg="#b7c2c7")
    root.resizable(False, False)

    # Create a label for the loading message
    loading_label = ttk.Label(root, text="Loading...", font=("Arial", 14), background="#b7c2c7")
    loading_label.pack(pady=50)

    # import logo

    image = Image.open(resource_path("Images\Manus.png"))
    image = image.resize((200, 200))
    img = ImageTk.PhotoImage(image)
    panel = tk.Label(root, image=img, bd=0)
    panel.pack()

    # Create a progress bar
    progress_bar = ttk.Progressbar(root, length=200, mode='indeterminate')
    progress_bar.pack()

    # Schedule closing the loading window after 3 seconds
    root.after(3000, close_loading)

    # Start the progress bar animation
    progress_bar.start(10)

    root.mainloop()


# Function that repeats every second to update the servos
async def update_servo(bt_socket, sVal):
    # Creates temporary list to compare previous servo values with current
    temp = [0, 0, 0, 0, 0, 0]
    # Loops endlessly until the program ends
    while True:
        # Creates list to be used for the temporary
        s = []
        # Number indexed used to define the index in the list and to select the servo No in Arduino Code
        num = 1
        # Loops through Values and gets the values adding them to the next temp list
        for x in sVal:
            a = int(x.get())
            s.append(a)
            # Comparing current values with previous and if they are different sends a command
            if a != temp[num - 1]:
                cmd = str(num) + " " + str(a)
                print(cmd)
                bt_socket.send(cmd.encode())

            num += 1
        temp = s
        await asyncio.sleep(1)


# Starts the loop with tkinter
def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def main():
    root = tk.Tk()
    root.title("Robotic arm")

    height = str(root.winfo_screenwidth())
    width = str(root.winfo_screenheight())
    root.geometry(height + "x" + width)

    T1 = tk.Label(root, text="Robotic Arm")
    T1.pack()

    sd1 = tk.DoubleVar()
    sd2 = tk.DoubleVar()
    sd3 = tk.DoubleVar()
    sd4 = tk.DoubleVar()
    sd5 = tk.DoubleVar()
    sd6 = tk.DoubleVar()

    sVal = [sd1, sd2, sd3, sd4, sd5, sd6]

    class servo:
        def __init__(self, servoNo):
            self.sNo = servoNo
            s = tk.Scale(root, from_=0, to=180, tickinterval=10, orient="horizontal", variable=sVal[servoNo - 1])
            s.set(0)
            s.pack(fill="x", padx="300")

    servo(1)
    servo(2)
    servo(3)
    servo(4)
    servo(5)
    servo(6)

    HC06_ADDRESS = "00:22:11:00:04:B8"
    PORT = 1  # Standard port for Bluetooth SPP

    # Create a Bluetooth socket
    bt_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

    # Connect to the HC-06
    bt_socket.connect((HC06_ADDRESS, PORT))

    # Creates asyncio event loop
    loop = asyncio.new_event_loop()
    asyncio.run_coroutine_threadsafe(update_servo(bt_socket, sVal), loop)

    # Runs this loop in a separate thread
    threading.Thread(target=start_loop, args=(loop,), daemon=True).start()

    root.mainloop()


# loading_page()
main()

