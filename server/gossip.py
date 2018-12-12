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
import dill
import pdb
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
SERVER_PRINT_STATE = False

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

@app.route('/getstate')
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
            s_print(colored("coming from {0}: port {1} => {2}".format(PORT, key, val[0]), "red"))
    # s_print(colored("rendering state from client: " + json.dumps(STATE), "green"))

build_state(PORT, PEER_PORTS)

books = open("books.txt", "r").read().split("\n")
favorite_book = random.choice(books)
version_number = 0
s_print("my favorite book is {0}".format(colored(favorite_book, "green")))
favorite_book = random.choice(books)
version_number = 0

# alice_key = RSA.generate(1024, Random.new().read)
# alice_privkey = alice_key.exportKey()
# alice_pubkey = alice_key.publickey().exportKey()
#
# bob_key = RSA.generate(1024, Random.new().read)
# bob_privkey = bob_key.exportKey()
# bob_pubkey = bob_key.publickey().exportKey()
#
# satoshi_key = RSA.generate(1024, Random.new().read)
# satoshi_privkey = satoshi_key.exportKey()
# satoshi_pubkey = satoshi_key.publickey().exportKey()
#
# blockchain = BlockChain(50, satoshi_pubkey, satoshi_privkey)
# genesis_block = blockchain.blocks()[0]
#
# txn1 = Transaction(satoshi_pubkey, alice_pubkey, 15, satoshi_privkey)
# txn2 = Transaction(satoshi_pubkey, bob_pubkey, 15, satoshi_privkey)
# new_block = Block([txn1, txn2], genesis_block.hash)
# blockchain.append(new_block)
#
# blockchain_bytes = dill.dumps(blockchain)
#
# favorite_book = blockchain_bytes
# version_number = 0
# s_print("blockchain is {0}".format(colored(favorite_book, "green")))

update_state({PORT: [favorite_book, version_number]})
render_state()

def select_books():
    global favorite_book
    global version_number
    while True:
        time.sleep(15)
        s_print("i don't like {0} anymore".format(colored(favorite_book, "green")))
        favorite_book = random.choice(books)
        s_print("my {0} favorite book is {1}".format(colored("new", "green"), colored(favorite_book, "green")))
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
                # s_print(colored("fetching update from {0}".format(port), "yellow"))
                try:
                    gossip_response = client.send_gossip(port, STATE)
                    # s_print(gossip_response.json())
                    update_state(gossip_response.json())
                    if STATE != PREVIOUS_STATE:
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
    # time.sleep(1)
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
    s = Thread(target=timer)
    s.daemon = True
    a = Thread(target=select_books)
    a.daemon = True
    a.start()
    f.start()
    s.start()
except KeyboardInterrupt as e:
    raise e
    pass
