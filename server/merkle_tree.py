# -*- coding: utf-8 -*-
import sys
import traceback
import hashlib
import pdb
import random

class Node(object):
    def __init__(self, txn):
        self._left = None
        self._right = None
        self._parent = None

    # Overrides the default implementation
	def __eq__(self, other):
		if isinstance(self, other.__class__):
			return self.__dict__ == other.__dict__
		return False

    def left(self):
        return self._left

    def right(self):
        return self._right

    def parent(self):
        return self._parent

    def data(self):
        return self._data

class HashLeaf(Node):
    def __init__(self, txn):
        Node.__init__(self, txn)
        self._txn = txn
        self._data = self.hash(txn.to_string())

    def txn(self):
        return self._txn

    def hash(self, txn):
        return hashlib.sha256(self.pad_txn(txn)).hexdigest()

    def pad_txn(self, txn):
        return "L"*len(txn) + txn + "LLL"*len(txn)

class HashNode(Node):
    def __init__(self, txn):
        Node.__init__(self, txn)
        self._data = self.hash(txn)

    def hash(self, txn):
        return hashlib.sha256(self.pad_txn(txn)).hexdigest()

    def pad_txn(self, txn):
        txn_length = len(txn) # int
        remainder = txn_length % 32 # int
        pad_length = 32 - remainder # int
        txn_length_digits = len(str(txn_length)) #int
        padding_block = "1" + "0"*(pad_length - 1 - txn_length_digits) + str(txn_length)
        return txn + padding_block

class MerkleTree(object):
    def __init__(self, txn_list):
        self._leaves = []
        self._nodes = []
        self._root = self.construct(txn_list)
        self._block_header = self._root.data

    def leaves(self):
        return self._leaves

    def nodes(self):
        return self._nodes

    def root(self):
        return self._root

    def construct(self, txns):
        if len(txns) == 1:
            self._leaves.append(HashLeaf(txns[0]))
            self._nodes.append(HashLeaf(txns[0]))
        else:
            for txn in txns:
                self._leaves.append(HashLeaf(txn))
                self._nodes.append(HashLeaf(txn))

            last_node = None
            if len(self._nodes) % 2 != 0:
                last_node = self._nodes.pop()

            idx = 0
            while idx < len(self._nodes):
                if idx < len(self._nodes) and idx + 1 < len(self._nodes):
                    child_one, child_two = self._nodes[idx], self._nodes[idx + 1]
                    parent = HashNode(child_one.data() + child_two.data())
                    child_one.parent, child_two.parent = parent, parent
                    parent.left, parent.right = child_one, child_two
                    # pdb.set_trace()
                    if isinstance(parent, Node):
                        self._nodes.append(parent)

                idx += 2

            if last_node is not None:
                root = HashLeaf(self._nodes[-1].data() + last_node.data())
                self._nodes.append(last_node)
                self._nodes.append(root)

        return self._nodes[-1]

def generate_merkle_proof(node):
    result = {}
    result["path"] = []
    result["txn"] = node.data()
    result["root"] = merkle_tree.root()

    current_node = node
    while isinstance(current_node, Node):
        parent = current_node.parent

        if isinstance(parent, Node):
            if parent.left == current_node:
                result["path"].append(parent.right)
            elif parent.right == current_node:
                result["path"].append(parent.left)
            else:
                raise Exception("tree is invalid")

        current_node = parent

    return result

def verify_merkle_proof(merkle_proof):
    path = merkle_proof["path"]
    result_hash = merkle_proof["txn"]
    for node in path:
        result_hash = node.parent.hash(result_hash + node.data())

    return merkle_proof["root"].data() == result_hash


# TEST CODE below:
if __name__ == "__main__":
    try:
        data = ["We", "hold", "these", "truths", "to", "be", "self-evident", "that"]
        merkle_tree = MerkleTree(data)
        tree_hashes = map(lambda node: node.data(), merkle_tree.nodes())
        print tree_hashes

        merkle_proof = generate_merkle_proof(merkle_tree.nodes()[0])
        proof_hashes = map(lambda node: node.data(), merkle_proof["path"])
        print proof_hashes
        # pdb.set_trace()
        print verify_merkle_proof(merkle_proof)
    except:
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)
