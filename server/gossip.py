import random
import requests
from flask import Flask, jsonify, request, make_response, render_template
from threading import Thread
from multiprocessing import Process, Manager, Value
from termcolor import colored
import time
import os
import sys
import json
import client
import signal
import pickle
import codecs
import uuid
import ipdb
from blockchain import *

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

PRIV_KEY = RSA.generate(1024, Random.new().read)
PUB_KEY = PRIV_KEY.publickey()
SERVER_PRINT_STATE = True

def s_print(msg):
    global SERVER_PRINT_STATE
    if SERVER_PRINT_STATE is True:
        print(msg)

app = Flask(__name__, static_folder="../client/static", template_folder="../client/templates")

@app.route('/')
def render_index():
    return render_template("index.html")

@app.route('/state')
def render_state():
    return render_template("state.html")

@app.route('/api/state')
def get_state():
    return jsonify(STATE)

@app.route('/gossip', methods=['POST'])
def gossip():
    new_state = request.data
    update_state(json.loads(new_state))
    # s_print(colored("rendering state from server:" + json.dumps(STATE), "red"))
    return jsonify(STATE)

@app.route('/getpubkey')
def get_pubkey():
    return PUB_KEY.exportKey()

if __name__ == "__main__":
    app.run()

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
    for port, msg_data in data.items():
        if port is None or msg_data is None:
            continue
        else:
            # add port to PEER_PORTS if PEER_PORTS count still less than than MAX_PEERS
            if len(PEER_PORTS) < MAX_PEERS and port not in PEER_PORTS:
                PEER_PORTS.append(port)
            STATE[port] = msg_data

def render_state():
    global PORT
    global STATE
    for peer_port, msg_data in STATE.items():
        if peer_port is not None and msg_data is not None:
            truncated_blockchain = msg_data["blockchain"][0:10]
            s_print(colored("coming from {0}: port {1} => {2}".format(PORT, peer_port, msg_data["parsed_blockchain"]), "red"))
    # s_print(colored("rendering state from client: " + json.dumps(STATE), "green"))

build_state(PORT, PEER_PORTS)

encoded_blockchain = open("seed.txt", "r").read()
blockchain = pickle.loads(codecs.decode(encoded_blockchain, "base64"))

version_number = 0
s_print("blockchain is {0}".format(colored(encoded_blockchain[0:10], "green")))

initial_state = {
    PORT: {
        "UUID": uuid.uuid4().int,
        "blockchain": encoded_blockchain,
        "parsed_blockchain": "{0}{1} block length: {2}, truncated base64: {3} {4}".format(blockchain.__repr__(), "{", len(blockchain.blocks()), encoded_blockchain[0:10], "}"),
        "mem_pool": [],
        "version_number": version_number,
        "ttl": time.time() + 60*1
    }
}

update_state(initial_state)
render_state()

def select_books():
    global encoded_blockchain
    global version_number
    while True:
        time.sleep(15)
        new_state = {
            "UUID": uuid.uuid4().int,
            "blockchain": encoded_blockchain,
            "parsed_blockchain": "{0}{1} block length: {2}, truncated base64: {3} {4}".format(blockchain.__repr__(), "{", len(blockchain.blocks()), encoded_blockchain[0:10], "}"),
            "mem_pool": [],
            "version_number": version_number + 1,
            "ttl": time.time() + 60*1
        }
        update_state({PORT: new_state})
        render_state()

def fetch_state():
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
                # s_print(colored("fetching update from {0}".format(port), "yellow"))
                try:
                    gossip_response = client.send_gossip(port, STATE)
                    # s_print(gossip_response.json())
                    update_state(gossip_response.json())
                    if STATE[port]["blockchain"] != PREVIOUS_STATE[port]["blockchain"]:
                        s_print(colored("new update from port {0}".format(port), "blue"))
                        render_state()
                        PREVIOUS_STATE = STATE.copy()
                    else:
                        # s_print(colored("no new update from port {0}".format(port), "blue"))
                        continue
                except StandardError as e:
                    failures += 1
                    if failures > 10:
                        s_print(colored("port {0} is no longer accepting incoming requests".format(port), "red"))
                        PEER_PORTS.remove(port)
                        new_port = random.choice(STATE.keys())
                        while new_port == port:
                            new_port = random.choice(STATE.keys())

                        if len(PEER_PORTS) < MAX_PEERS:
                            PEER_PORTS.append(new_port)
                            s_print(colored("port {0} has been added to the peer list".format(new_port), "red"))
                        failures = 0

def timer():
    global STATE
    s_print(colored("STARTING TIMER", "yellow"))
    start = time.time()
    while len(STATE.keys()) < 9:
        time.sleep(1)
    end = time.time()
    s_print(colored("END TIMER: {0} sec".format(end - start), "yellow"))
    time.sleep(1)
    pid = os.getpid()
    os.kill(pid, signal.SIGINT)

try:
    f = Thread(target=fetch_state)
    f.daemon = True
    timer = Thread(target=timer)
    timer.daemon = True
    s = Thread(target=select_books)
    s.daemon = True
    s.start()
    f.start()
    timer.start()
except KeyboardInterrupt as e:
    raise e
    pass
