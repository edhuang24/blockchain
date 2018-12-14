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

# ===========BEGIN: SET GLOBAL VARIABLES & HELPERS=========== #

STATE = {}
PREVIOUS_STATE = {}
TIMES = {}
DEBUG = False
MAX_PEERS = 5

priv_key = RSA.generate(1024, Random.new().read)
PRIV_KEY = priv_key.exportKey()
PUB_KEY = priv_key.publickey().exportKey()
SERVER_PRINT_STATE = True

# ===========END: SET GLOBAL VARIABLES & HELPERS=========== #

# ===========BEGIN: FLASK SERVER LOGIC=========== #

app = Flask(__name__, static_folder="../client/static", template_folder="../client/templates")

@app.route('/')
def render_index():
    return render_template("index.html")

@app.route('/state')
def render_state():
    return render_template("state.html")

@app.route('/gossip', methods=['POST'])
def gossip():
    global STATE
    new_state = request.data
    update_state(json.loads(new_state))
    # s_print(colored("rendering state from server:" + json.dumps(STATE), "red"))
    return jsonify(STATE)

@app.route('/api/getpubkey')
def get_pubkey():
    return PUB_KEY.exportKey()

@app.route('/api/state')
def get_state():
    return jsonify(STATE)

@app.route('/api/balances')
def get_balances():
    global BLOCKCHAIN
    return jsonify(BLOCKCHAIN.state())

if __name__ == "__main__":
    app.run()

# ===========END: FLASK SERVER LOGIC=========== #

# ===========BEGIN: BLOCKCHAIN HELPERS=========== #

def s_print(msg):
    global SERVER_PRINT_STATE
    if SERVER_PRINT_STATE is True:
        print(msg)

def encode_object(object):
    bytes = pickle.dumps(object)
    return codecs.encode(bytes, "base64")

def decode_object(encoded_object):
    decoded = codecs.decode(encoded_object, "base64")
    return pickle.loads(decoded)

def parse_blockchain(blockchain):
    return "{0}{1} block length: {2}, truncated base64: {3} {4}".format(blockchain.__repr__(), "{", len(blockchain.blocks()), encoded_blockchain[0:10], "}")

# ===========END: BLOCKCHAIN HELPERS=========== #

# ===========BEGIN: INITIALIZE STATE=========== #

# PORT, PEER_PORTS = sys.argv[1], sys.argv[2]
PORT, peer_ports = os.environ.get("PORT"), os.environ.get("PEER_PORTS")
PEER_PORTS = []

satoshi_pubkey = open("satoshi_pubkey.txt").read()
satoshi_privkey = open("satoshi_privkey.txt").read()

encoded_blockchain = open("seed.txt", "r").read()
BLOCKCHAIN = decode_object(encoded_blockchain)

s_print("blockchain is {0}".format(colored(encoded_blockchain[0:10], "green")))

initial_state = {
    PORT: {
        "UUID": uuid.uuid4().int,
        "originating_port": PORT,
        "blockchain": encode_object(BLOCKCHAIN),
        "parsed_blockchain": parse_blockchain(BLOCKCHAIN),
        "mem_pool": [],
        "version_number": 0,
        "ttl": time.time() + 60*1
    }
}

# ===========END: INITIALIZE STATE=========== #

# ===========BEGIN: SERVER HELPERS=========== #

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
    global version_number
    STATE[port] = None
    if len(peer_ports) > 0:
        for peer_port in peer_ports:
            if peer_port is not None:
                STATE[peer_port] = None

# TODO: REFACTOR THIS TO USE PEER_PORTS INSTEAD OF FLOODING
def update_state(data):
    global STATE
    global MEM_POOL
    global BLOCKCHAIN
    global DEBUG
    global version_number
    for port, msg_data in data.items():
        if port is None or msg_data is None:
            continue
        else:
            # add port to PEER_PORTS if PEER_PORTS count still less than than MAX_PEERS
            if len(PEER_PORTS) < MAX_PEERS and port not in PEER_PORTS:
                PEER_PORTS.append(port)

            if port not in STATE.keys() or STATE[port] is None:
                STATE[port] = msg_data

            if STATE[port]["version_number"] < msg_data["version_number"]:
                STATE[port] = msg_data
                msg_blockchain = decode_object(msg_data["blockchain"])
                self_len = len(BLOCKCHAIN.blocks())
                new_blocks = msg_blockchain.blocks()[self_len:]
                fork_executed = BLOCKCHAIN.decide_fork(msg_blockchain)
                # iterate over the blocks & leaves to grab the txns
                if fork_executed is True:
                    for block in new_blocks:
                        for leaf in block.leaves():
                            encoded_txn = encode_object(leaf.txn())
                            if encoded_txn in MEM_POOL:
                                # remove the new transactions from my mempool so I don't mine them later
                                # NOTE: they should have already been removed from the peer mempool when they were mined by the peer
                                STATE[PORT]["mem_pool"].remove(encode_object(leaf.txn()))

            # after flushing my mempool, combine it with other mempool
            combined_mempool = list(set(STATE[PORT]["mem_pool"] + msg_data["mem_pool"]))
            MEM_POOL = combined_mempool

def render_state():
    global PORT
    global STATE
    for port, msg_data in STATE.items():
        if port is not None and msg_data is not None:
            truncated_blockchain = msg_data["blockchain"][0:10]
            s_print(colored("coming from {0}: port {1} => {2}, version: {3}".format(PORT, port, msg_data["parsed_blockchain"], msg_data["version_number"]), "red"))
    # s_print(colored("rendering state from client: " + json.dumps(STATE), "green"))

# ===========BEGIN: SERVER HELPERS=========== #

# ===========BEGIN: SERVER PROCEDURES=========== #

build_state(PORT, PEER_PORTS)
update_state(initial_state)
render_state()

def evaluate_state():
    global STATE
    global MEM_POOL
    global BLOCKCHAIN
    global DEBUG
    while True:
        if DEBUG is True:
            time.sleep(1000)
        # sec = random.randint(1, 15)
        sec = 3
        print(colored("sleeping {0} sec".format(sec), "yellow"))
        time.sleep(sec)

        new_state = {
            "UUID": uuid.uuid4().int,
            "originating_port": PORT,
            "blockchain": encode_object(BLOCKCHAIN),
            "parsed_blockchain": parse_blockchain(BLOCKCHAIN),
            "mem_pool": STATE[PORT]["mem_pool"],
            "version_number": STATE[PORT]["version_number"] + 1,
            "ttl": time.time() + 60*1
        }

        if len(MEM_POOL) > 1:
            txns = MEM_POOL[:2]
            txns = map(lambda txn: decode_object(txn), txns)
            latest_block = BLOCKCHAIN.blocks()[-1]
            new_block = Block(txns, latest_block.hash())
            appended = BLOCKCHAIN.append(new_block)
            print(appended)
            if appended is True:
                new_state["mem_pool"] = MEM_POOL[2:]
                new_state["blockchain"] = encode_object(BLOCKCHAIN)
                new_state["parsed_blockchain"] = parse_blockchain(BLOCKCHAIN)
        else:
            new_txn = Transaction(satoshi_pubkey, PUB_KEY, 50, satoshi_privkey)
            encoded_txn = encode_object(new_txn)
            new_state["mem_pool"].append(encoded_txn)

        update_state({PORT: new_state})
        render_state()


def fetch_state():
    global STATE
    global DEBUG
    global PREVIOUS_STATE
    global PEER_PORTS
    global MAX_PEERS
    failures = 0
    while True:
        if DEBUG is True:
            time.sleep(1000)
        time.sleep(2)
        for port, book_data in STATE.items():
            if port == PORT:
                continue
            if port in PEER_PORTS:
                try:
                    # s_print(colored("fetching update from {0}".format(port), "yellow"))
                    gossip_response = client.send_gossip(port, STATE)
                    # s_print(gossip_response.json())
                    update_state(gossip_response.json())
                except StandardError as e:
                    failures += 1
                    if failures > 100:
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

# ===========BEGIN: SERVER PROCEDURES=========== #

try:
    f = Thread(target=fetch_state)
    f.daemon = True
    timer = Thread(target=timer)
    timer.daemon = True
    s = Thread(target=evaluate_state)
    s.daemon = True
    s.start()
    f.start()
    timer.start()
except KeyboardInterrupt as e:
    raise e
    pass
