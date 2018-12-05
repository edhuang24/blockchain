import random
import requests
from flask import Flask, jsonify, request, make_response
from threading import Thread
from multiprocessing import Process, Manager, Value
from termcolor import colored
import time
import os
import sys
import json
import client
import signal
import pdb

# message = [favorite_book, version_number]
# state = {
#     port1: [favorite_book, version_number],
#     port2: [favorite_book, version_number],
#     port3: [favorite_book, version_number],
#     port4: [favorite_book, version_number]
# }

STATE = {}
PREVIOUS_STATE = {}
TIMES = {}
MAX_PEERS = 5

app = Flask(__name__, static_folder="/")

@app.route('/gossip', methods=['POST'])
def gossip():
    new_state = request.data
    update_state(json.loads(new_state))
    # print(colored("rendering state from server:" + json.dumps(STATE), "red"))
    return jsonify(STATE)

# STATE = state.STATE
# PORT, PEER_PORTS = sys.argv[1], sys.argv[2]
PORT, peer_ports = os.environ.get("PORT"), os.environ.get("PEER_PORTS")
PEER_PORTS = []

if peer_ports is not None:
    peer_ports = peer_ports.split(",")
    PEER_PORTS.append(random.choice(peer_ports))
    PEER_PORTS.append(random.choice(peer_ports))
    PEER_PORTS.append(random.choice(peer_ports))
    if PORT in PEER_PORTS:
        PEER_PORTS.remove(PORT)
    PEER_PORTS = list(set(PEER_PORTS))

def build_state(port, peer_ports):
    global STATE
    STATE[port] = None
    if len(peer_ports) > 0:
        for peer_port in peer_ports:
            if peer_port is not None:
                STATE[peer_port] = None

def update_state(data):
    global STATE
    for port, book_data in data.items():
        if port is None or book_data is None:
            continue
        else:
            # add port to PEER_PORTS if PEER_PORTS count still less than than MAX_PEERS
            if len(PEER_PORTS) < MAX_PEERS and port not in PEER_PORTS:
                PEER_PORTS.append(port)
            STATE[port] = book_data

def render_state():
    global PORT
    global STATE
    for key, val in STATE.items():
        if key is not None and val is not None:
            print(colored("coming from {0}: port {1} => {2}".format(PORT, key, val[0]), "red"))
    # print(colored("rendering state from client: " + json.dumps(STATE), "green"))

build_state(PORT, PEER_PORTS)

books = open("books.txt", "r").read().split("\n")

favorite_book = random.choice(books)
version_number = 0
print("my favorite book is {0}".format(colored(favorite_book, "green")))
update_state({PORT: [favorite_book, version_number]})
render_state()

def select_books():
    global favorite_book
    global version_number
    while True:
        time.sleep(100)
        print("i don't like {0} anymore".format(colored(favorite_book, "green")))
        favorite_book = random.choice(books)
        print("my {0} favorite book is {1}".format(colored("new", "green"), colored(favorite_book, "green")))
        version_number += 1
        update_state({PORT: [favorite_book, version_number]})
        render_state()

def fetch_state():
    # time.sleep(1)
    global STATE
    global PREVIOUS_STATE
    global PEER_PORTS
    global MAX_PEERS
    failures = 0
    while True:
        time.sleep(5)
        for port, book_data in STATE.items():
            if port == PORT:
                continue
            if port in PEER_PORTS:
                # print(colored("fetching update from {0}".format(port), "yellow"))
                try:
                    gossip_response = client.send_gossip(port, STATE)
                    # print(gossip_response.json())
                    update_state(gossip_response.json())
                    if STATE != PREVIOUS_STATE:
                        print(colored("new update from port {0}".format(port), "blue"))
                        render_state()
                        PREVIOUS_STATE = STATE.copy()
                    else:
                        # print(colored("no new update from port {0}".format(port), "blue"))
                        continue
                except StandardError as e:
                    failures += 1
                    if failures > 10:
                        print(colored("port {0} is no longer accepting incoming requests".format(port), "red"))
                        PEER_PORTS.remove(port)
                        new_port = random.choice(STATE.keys())
                        while new_port == port:
                            new_port = random.choice(STATE.keys())

                        if len(PEER_PORTS) < MAX_PEERS:
                            PEER_PORTS.append(new_port)
                            print(colored("port {0} has been added to the peer list".format(new_port), "red"))
                        failures = 0

def timer():
    # time.sleep(1)
    global STATE
    print(colored("STARTING TIMER", "yellow"))
    start = time.time()
    while len(STATE.keys()) < 9:
        time.sleep(1)
    end = time.time()
    print(colored("END TIMER: {0} sec".format(end - start), "yellow"))
    time.sleep(1)
    pid = os.getpid()
    os.kill(pid, signal.SIGINT)


try:
    # Thread(target=select_books).start()
    f = Thread(target=fetch_state)
    f.daemon = True
    s = Thread(target=timer)
    s.daemon = True
    f.start()
    s.start()
except KeyboardInterrupt as e:
    raise e
    pass
