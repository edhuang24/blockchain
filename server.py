from flask import Flask, jsonify, request, make_response
from termcolor import colored
import state
import json
import pdb
import os

STATE = state.STATE
PORT = os.environ.get("PORT")

def update_state(data):
    global STATE
    # pdb.set_trace()
    for port, movie_data in data.items():
        if port is None and movie_data is None:
            STATE[PORT] = None
        else:
            STATE[PORT] = movie_data

app = Flask(__name__, static_folder="/")

@app.route('/gossip', methods=['POST'])
def gossip():
    pdb.set_trace()
    new_state = request.data
    update_state(json.loads(new_state))
    print(colored(json.dumps(STATE), "red"))
    return make_response(jsonify(STATE), 200)
