import random
import socket

IP_ADDRESS = "127.0.0.1"
PORT = 5000

c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    msg = raw_input("Enter a message to send: ")

    c.sendto(msg, (IP_ADDRESS, PORT))

    data, addr = c.recvfrom(1024)
    print 'Server reply: ' + data
