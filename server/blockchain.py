import sys
import traceback
import hashlib
import pdb
import Crypto
import random
from termcolor import colored
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from base64 import b64decode, b64encode
from merkle_tree import *
from proof_of_work import *

class Transaction(object):
    def __init__(self, from_address, to_address, amount, private_key):
        self._from = from_address
        self._to = to_address
        self._amount = amount
        self._signature = self.sign(self.digest(), private_key)

    def validate_signature(self):
        if self._from == None:
            return True
        else:
            pub_key = RSA.importKey(self._from)
            verifier = PKCS1_v1_5.new(pub_key)
            return verifier.verify(self.digest(), self._signature)

    def from_address(self):
        return self._from

    def to_address(self):
        return self._to

    def amount(self):
        return self._amount

    def signature(self):
        return self._signature

    def sign(self, digest, private_key):
        priv_key = RSA.importKey(private_key)
        signer = PKCS1_v1_5.new(priv_key)
        return signer.sign(digest)

    def raw_string(self):
        return str(self._from) + str(self._to) + str(self._amount)

    def digest(self):
        return SHA256.new(self.raw_string())

    def to_string(self):
        return self.digest().hexdigest()

class Block(object):
    def __init__(self, transactions, previous_hash):
        if self.validate_transactions(transactions):
            merkle_tree = MerkleTree(transactions)
            self._leaves = merkle_tree.leaves()
            self._root = merkle_tree.root()
            self._previous_hash = previous_hash
            self._nonce = None
            self._hash = None
            self._timestamp = None
            txns_string = "".join(map(lambda txn: txn.to_string(), transactions))
            self.mint(txns_string, 1)
        else:
            return

    def leaves(self):
        return self._leaves

    def root(self):
        return self._root

    def nonce(self):
        return self._nonce

    def hash(self):
        return self._hash

    def timestamp(self):
        return self._timestamp

    def mint(self, challenge, work_factor):
        token = mint(challenge, work_factor)
        self._hash = token[0]
        self._nonce = token[1]
        self._timestamp = time.ctime() # make sure not to use time.time()

    def create_genesis_block(self, to_address, amount, priv_key):
        genesis_txn = Transaction(None, to_address, 50, priv_key)
        return Block([genesis_txn], None)

    def validate_transactions(self, transactions):
        for txn in transactions:
            if txn.from_address() is not None:
                if txn.validate_signature() == False:
                    return False
        return True

    def validate_nonce(self, nonce):
        txns = map(lambda leaf: leaf.txn(), self._leaves)
        txns_string = "".join(map(lambda txn: txn.to_string(), txns))
        token_hash = hashlib.sha256(str(txns_string) + str(self._timestamp) + str(nonce)).hexdigest()
        # pdb.set_trace()
        return token_hash == self.hash()

class BlockChain(object):
    def __init__(self, amount, pub_key, priv_key):
        self._blocks = []
        self._state = {}
        genesis_txn = Transaction(None, pub_key, 50, priv_key)
        self._genesis = Block([genesis_txn], None)
        self.append(self._genesis)

    def blocks(self):
        return self._blocks

    def append(self, block):
        if self.validate_block(block) is True:
            self.execute_txns(block)
            print(colored(self._state, "green"))
            self._blocks.append(block)
        else:
            raise Exception("Block is invalid")

    # need to separate the validation from the execution
    def validate_block(self, block):
        if block == self._genesis:
            return True

        for leaf in block.leaves():
            if leaf.txn().from_address() is not None and leaf.txn().from_address() in self._state:
                if (self._state[leaf.txn().from_address()] - leaf.txn().amount()) < 0:
                    return False
            elif leaf.txn().from_address() is None or leaf.txn().from_address() not in self._state:
                return False

        return True

    def validate_blockchain(self, blockchain):
        for block in blockchain:
            if validate_block(block) == False:
                return False
            if block.validate_nonce(block.nonce()) == False:
                return False
            for leaf in block.leaves():
                if leaf.txn().validate_signature() == False:
                    return False

        return True

    def execute_txns(self, block):
        for leaf in block.leaves():
            if block != self._genesis:
                self._state[leaf.txn().from_address()] -= leaf.txn().amount()

            if leaf.txn().to_address() not in self._state:
                self._state[leaf.txn().to_address()] = 0

            self._state[leaf.txn().to_address()] += leaf.txn().amount()

    def decide_fork(self, blockchain):
        if validate_blockchain(blockchain) is True and len(blockchain.blocks()) > len(self._blocks):
            return True
        else:
            print("Blockchain is invalid or not longer than current chain")
            return False

    def execute_fork(self, blockchain):
        if decide_fork(blockchain) is True:
            self._blocks = blockchain.blocks()
            self._state = {}
            map(lambda block: self.execute_txns(block), self._blocks)
        else:
            print("No fork will be executed")
            raise Exception("Fork aborted")

# TEST CODE here
if __name__ == "__main__":
    try:
        alice_key = RSA.generate(1024, Random.new().read)
        alice_privkey = alice_key.exportKey()
        alice_pubkey = alice_key.publickey().exportKey()
        bob_key = RSA.generate(1024, Random.new().read)
        bob_privkey = bob_key.exportKey()
        bob_pubkey = bob_key.publickey().exportKey()
        txn1 = Transaction(alice_pubkey, bob_pubkey, 10, alice_privkey)
        print(txn1.validate_signature())

        satoshi_key = RSA.generate(1024, Random.new().read)
        satoshi_privkey = satoshi_key.exportKey()
        satoshi_pubkey = satoshi_key.publickey().exportKey()
        blockchain = BlockChain(50, satoshi_pubkey, satoshi_privkey)

        txn1 = Transaction(satoshi_pubkey, alice_pubkey, 15, satoshi_privkey)
        txn2 = Transaction(satoshi_pubkey, bob_pubkey, 15, satoshi_privkey)
        genesis_block = blockchain.blocks()[0]
        print(genesis_block.validate_nonce(genesis_block.nonce()))
        new_block = Block([txn1, txn2], genesis_block.hash)
        blockchain.append(new_block)
        pdb.set_trace()
    except:
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)
