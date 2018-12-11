from gossip import GossipNode

# port for this node
port = 5020
# ports for the nodes connected to this node
connected_nodes = [5000]

node = GossipNode(port, connected_nodes)
node.peers = [5000, 5010, 5020]
