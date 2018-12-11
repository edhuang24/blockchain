import requests
import json

def send_gossip(port, state):
    return requests.post("http://localhost:{0}/gossip".format(port), data = json.dumps(state))
