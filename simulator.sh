# !/bin/sh
port=1024
osascript -e "tell application \"Terminal\"
    do script \"cd /Users/ehuang/Desktop/gossip-protocol; export FLASK_APP=gossip.py; PORT=$port flask run --port=$port;\"
end tell"
sleep 5

port2=$(($port + 1))
osascript -e "tell application \"Terminal\"
    do script \"cd /Users/ehuang/Desktop/gossip-protocol; export FLASK_APP=gossip.py; PORT=$port2 PEER_PORT=$port flask run --port=$port;\"
end tell"
sleep 3

port3=$(($port + 2))
osascript -e "tell application \"Terminal\"
    do script \"cd /Users/ehuang/Desktop/gossip-protocol; export FLASK_APP=gossip.py; PORT=$port3 PEER_PORT=$port flask run --port=$port;\"
end tell"
sleep 3

ports=$(seq 1027 1033)
ports_array=($ports)
for port in $ports; do
  sleep 2
  peer_port1=${ports_array[$RANDOM % 7]}
  peer_port2=${ports_array[$RANDOM % 7]}
  peer_port3=${ports_array[$RANDOM % 7]}
  osascript -e "tell application \"Terminal\"
      do script \"cd /Users/ehuang/Desktop/gossip-protocol; export FLASK_APP=gossip.py; PORT=$port PEER_PORT=$peer_port1,$peer_port2,$peer_port3 flask run --port=$port;\"
  end tell"
done
