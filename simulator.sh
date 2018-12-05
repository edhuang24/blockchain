# !/bin/sh
port=1024
osascript -e "tell application \"Terminal\"
    do script \"cd /Users/ehuang/Desktop/gossip-protocol; export FLASK_APP=gossip.py; PORT=$port flask run --port=$port;\"
end tell"
sleep 1

port2=$(($port + 1))
osascript -e "tell application \"Terminal\"
    do script \"cd /Users/ehuang/Desktop/gossip-protocol; export FLASK_APP=gossip.py; PORT=$port2 PEER_PORTS=$port flask run --port=$port2;\"
end tell"
sleep 1

port3=$(($port + 2))
osascript -e "tell application \"Terminal\"
    do script \"cd /Users/ehuang/Desktop/gossip-protocol; export FLASK_APP=gossip.py; PORT=$port3 PEER_PORTS=$port,$port2 flask run --port=$port3;\"
end tell"
sleep 1

ports=$(seq 1027 1032)
ports_array=($(seq 1024 1032))
for port in $ports; do
  # sleep 2
  peer_port1=${ports_array[$RANDOM % 7]}
  peer_port2=${ports_array[$RANDOM % 7]}
  peer_port3=${ports_array[$RANDOM % 7]}
  peer_port4=${ports_array[$RANDOM % 7]}
  peer_port5=${ports_array[$RANDOM % 7]}
  osascript -e "tell application \"Terminal\"
      do script \"cd /Users/ehuang/Desktop/gossip-protocol; export FLASK_APP=gossip.py; PORT=$port PEER_PORTS=$peer_port1,$peer_port2,$peer_port3,$peer_port4,$peer_port5 flask run --port=$port;\"
  end tell"
done
