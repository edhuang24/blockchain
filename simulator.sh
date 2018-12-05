#!/bin/sh
port=1024
osascript -e "tell application \"Terminal\"
    do script \"cd /Users/ehuang/Desktop/gossip-protocol; export FLASK_APP=gossip.py; PORT=${port} flask run --port=$port;\"
end tell"
sleep 5

for port in {$port..$((port + 5))}; do
  
  osascript -e "tell application \"Terminal\"
      do script \"cd /Users/ehuang/Desktop/gossip-protocol; export FLASK_APP=gossip.py; PORT=${port} PEER_PORT=$peer_port flask run --port=$port;\"
  end tell"
done
