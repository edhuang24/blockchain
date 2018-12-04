#!/bin/sh
port=1024
osascript -e "tell application \"Terminal\"
    do script \"cd /Users/ehuang/Desktop/gossip-protocol; export FLASK_APP=gossip.py; PORT=${port} flask run --port=$port;\"
end tell"
sleep 5
port=1025
peer_port=1024
osascript -e "tell application \"Terminal\"
    do script \"cd /Users/ehuang/Desktop/gossip-protocol; export FLASK_APP=gossip.py; PORT=${port} PEER_PORT=$peer_port flask run --port=$port;\"
end tell"

# for port in {1000..1001}; do
#   case $port in
#     $1000)
#       ;;
#     $1001)
#       peer_port=1000
#       ;;
#   esac
#   osascript -e "tell application \"Terminal\"
#       do script \"cd /Users/ehuang/Desktop/gossip-protocol; export FLASK_APP=gossip.py; PORT=${port} PEER_PORT=$peer_port flask run --port=$port;\"
#   end tell"
# done
