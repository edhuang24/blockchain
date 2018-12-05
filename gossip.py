import random
import requests
from flask import Flask, jsonify, request, make_response
from threading import Thread
import time
import pdb
import os
import sys
from termcolor import colored
import json
import client

# message = [favorite_movie, version_number]
# state = {
#     port1: [favorite_movie, version_number],
#     port2: [favorite_movie, version_number],
#     port3: [favorite_movie, version_number],
#     port4: [favorite_movie, version_number]
# }

STATE = {}
PREVIOUS_STATE = {}
MAX_PEERS = 3

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
    for port, movie_data in data.items():
        if port is None or movie_data is None:
            continue
        else:
            STATE[port] = movie_data

def render_state():
    global PORT
    global STATE
    for key, val in STATE.items():
        if key is not None and val is not None:
            print(colored("coming from {0}: port {1} => {2}".format(PORT, key, val[0]), "red"))
    # print(colored("rendering state from client: " + json.dumps(STATE), "green"))

build_state(PORT, PEER_PORTS)

movies = open("movies.txt", "r").read().split("\n")

favorite_movie = random.choice(movies)
version_number = 0
print("my favorite movie is {0}".format(colored(favorite_movie, "green")))
update_state({PORT: [favorite_movie, version_number]})
render_state()

def select_books():
    global favorite_movie
    global version_number
    while True:
        try:
            time.sleep(15)
            print("i don't like {0} anymore".format(colored(favorite_movie, "green")))
            favorite_movie = random.choice(movies)
            print("my {0} favorite movie is {1}".format(colored("new", "green"), colored(favorite_movie, "green")))
            version_number += 1
            update_state({PORT: [favorite_movie, version_number]})
            render_state()
        except KeyboardInterrupt:
            break

def fetch_state():
    global STATE
    global PREVIOUS_STATE
    while True:
        try:
            time.sleep(5)
            for port, movie_data in STATE.items():
                if port == PORT:
                    continue
                print(colored("fetching update from {0}".format(port), "yellow"))
                gossip_response = client.send_gossip(port, STATE)
                update_state(gossip_response.json())
                if STATE != PREVIOUS_STATE:
                    print(colored("new update for port {0}".format(port), "blue"))
                    render_state()
                    PREVIOUS_STATE = STATE
                else:
                    print(colored("no new update from port {0}".format(port), "blue"))
        except KeyboardInterrupt:
            break

Thread(target=select_books).start()
Thread(target=fetch_state).start()
