import socket

HC06_ADDRESS = "00:22:11:00:04:B8"
PORT = 1  # Standard port for Bluetooth SPP

# Create a Bluetooth socket
bt_socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

# Connect to the HC-06
bt_socket.connect((HC06_ADDRESS, PORT))

x = ""

while x != "end":
    x = input("Enter")
    bt_socket.send(x.encode())

bt_socket.close()