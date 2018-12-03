import random
import requests
import socket
from threading import Thread
import time
import pdb
# from flask import Flask, render_template, jsonify, request, make_response, send_from_directory

class GossipNode:
    infected_nodes = []

    def __init__(self, port, connected_nodes):
        self.socket = socket.socket(type=socket.SOCK_DGRAM)
        self.hostname = socket.gethostname()
        self.port = port
        self.socket.bind((self.hostname, self.port))
        self.version = 0
        self.cache = []
        self.peers = []

        self.susceptible_nodes = connected_nodes
        print(f"Node started on port {self.port}")
        print(f"susceptible notes: {self.susceptible_nodes}")
        self.start_threads()

    def port(self):
        return self.port

    def get_peers(self, port):
        # breakpoint()
        message = "get peers"
        self.socket.sendto(message.encode('ascii'), (self.hostname, port))

    # def set_peers(self, new_peers = []):
    #     self.peers.append(new_peers)
    #     return self.peers

    def input_message(self):
        while True:
            message_to_send = input("Enter a message to send:\n")
            self.transmit_message(message_to_send)

    def transmit_message(self, message):
        while self.susceptible_nodes:
            selected_port = random.choice(self.susceptible_nodes)

            print("\n")
            print("-"*50)
            print(f"Susceptible nodes => {self.susceptible_nodes}")
            print(f"Infected nodes => {GossipNode.infected_nodes}")
            print(f"Peers => {self.peers}")
            print(f"Port selected is [{selected_port}]")

            self.socket.sendto(message.encode('ascii'), (self.hostname, selected_port))

            print(f"Message: '{message}' sent to [{selected_port}].")
            print(f"Susceptible nodes => {self.susceptible_nodes}")
            print(f"Infected nodes => {GossipNode.infected_nodes}")
            print("-"*50)
            time.sleep(2)
            print("\n")

    def receive_message(self):
        # breakpoint()
        while True:
            message, address = self.socket.recvfrom(1024)

            if message.decode('ascii') == "get peers":
                if address[1] not in self.peers:
                    self.peers.append(address[1])
                self.socket.sendto(f"send peers: {self.peers}", (self.hostname, address[1]))
            elif "send peers:" in message.decode('ascii'):
                pdb.set_trace()
                self.peers.append(message.slice(11, len(message)))
            else:
                if address[1] in self.susceptible_nodes:
                    self.susceptible_nodes.remove(address[1])
                    GossipNode.infected_nodes.append(address[1])

                time.sleep(2)

                print(f"\nMessage is: '{message.decode('ascii')}'.\nReceived at [{time.ctime(time.time())}] from [{address[1]}]\n")

                self.transmit_message(message)

    def start_threads(self):
        Thread(target=self.input_message).start()
        Thread(target=self.receive_message).start()

        # @app.route('/peers')
        # def peers():
        #     return "get peers"
        #
        # @app.route('/gossip')
        # def gossip():
        #     return "post gossip"

# message = {
#     uuid: 1,
#     port: 5000,
#     version: 1,
#     TTL: 60000,
#     data: "a book"
# }
