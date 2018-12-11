import random
import socket

IP_ADDRESS = "127.0.0.1"
PORT = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

s.bind((IP_ADDRESS, PORT))

while True:
    data, addr = s.recvfrom(1024)
    # print "Message: ", data

    if not data:
        break

    reply = 'OK...' + data
    s.sendto(reply, addr)
    print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()

s.close()
