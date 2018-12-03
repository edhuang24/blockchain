from gossip import GossipNode

# port for this node
port = 5010
# ports for the nodes connected to this node
connected_nodes = [5000]
node = GossipNode(port, connected_nodes)
# node.get_peers(connected_nodes[0])
