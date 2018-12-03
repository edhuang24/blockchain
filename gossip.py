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
# import state
import client

# message = [favorite_movie, version_number]
# state = {
#     port1: [favorite_movie, version_number],
#     port2: [favorite_movie, version_number],
#     port3: [favorite_movie, version_number],
#     port4: [favorite_movie, version_number]
# }

STATE = {}

app = Flask(__name__, static_folder="/")

@app.route('/gossip', methods=['POST'])
def gossip():
    new_state = request.data
    # pdb.set_trace()
    update_state(json.loads(new_state))
    # print(colored("rendering state from server:" + json.dumps(STATE), "red"))
    return jsonify(STATE)

# STATE = state.STATE
# PORT, PEER_PORT = sys.argv[1], sys.argv[2]
PORT, PEER_PORT = os.environ.get("PORT"), os.environ.get("PEER_PORT")

def build_state(port, peer_port):
    global STATE
    STATE[port] = None
    if peer_port is not None:
        STATE[peer_port] = None
    # pdb.set_trace()

def update_state(data):
    global STATE
    for port, movie_data in data.items():
        if port is None or movie_data is None:
            continue
        else:
            STATE[port] = movie_data

def render_state():
    global STATE
    for key, val in STATE.items():
        if key is not None and val is not None:
            print(colored("port {0} likes to watch {1}".format(key, val[0]), "red"))
    # print(colored("rendering state from client: " + json.dumps(STATE), "green"))

# Thread = Thread(target=build_state(PORT, PEER_PORT)).start()
build_state(PORT, PEER_PORT)

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
        time.sleep(10)
        print("i don't like {0} anymore".format(colored(favorite_movie, "green")))
        favorite_movie = random.choice(movies)
        print("my {0} favorite movie is {1}".format(colored("new", "green"), colored(favorite_movie, "green")))
        version_number += 1
        update_state({PORT: [favorite_movie, version_number]})
        # for port, movie_data in STATE.items():
        #     if port == PORT:
        #         continue
        #     gossip_response = send_gossip(port, STATE)
        #     update_state(gossip_response.json())
        render_state()

def fetch_state():
    global STATE
    while True:
        time.sleep(5)
        for port, movie_data in STATE.items():
            if port == PORT:
                continue
            print(colored("fetching update from {0}".format(port)))
            gossip_response = client.send_gossip(port, STATE)
            # pdb.set_trace()
            update_state(gossip_response.json())
            render_state()

Thread(target=select_books).start()
Thread(target=fetch_state).start()
