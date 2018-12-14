import Crypto
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from base64 import b64decode, b64encode
from merkle_tree import *
from proof_of_work import *

class Transaction(object):
    def __init__(self, from_address, to_address, amount, private_key):
        # ipdb.set_trace()
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
        """
        initialize with array of transactions and the hash of the previous block
        """
        # ipdb.set_trace()
        if self.validate_transactions(transactions):
            merkle_tree = MerkleTree(transactions)
            self._leaves = merkle_tree.leaves()
            self._root = merkle_tree.root()
            self._previous_hash = previous_hash
            self._nonce = None
            self._hash = None
            self._timestamp = None
            txns_string = "".join(map(lambda txn: txn.to_string(), transactions))
            # NOTE: this is where the work factor is inserted
            self.block_mint(txns_string, 4)
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

    def block_mint(self, challenge, work_factor):
        token = mint(challenge, work_factor)
        self._hash = token[0]
        self._nonce = token[1]
        self._timestamp = token[2] # make sure not to use time.time()

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
        # ipdb.set_trace()
        return token_hash == self.hash()

class BlockChain(object):
    def __init__(self, amount, pub_key, priv_key):
        self._blocks = []
        self._state = {}
        genesis_txn = Transaction(None, pub_key, amount, priv_key)
        self._genesis = Block([genesis_txn], None)
        self.append(self._genesis)

    def len(self):
        return len(self._blocks)

    def blocks(self):
        return self._blocks

    def state(self):
        return self._state

    def print_state(self):
        print(colored(self._state, "green"))

    def append(self, block):
        if self.validate_block(block) is True:
            self.execute_txns(block)
            # self.print_state()
            self._blocks.append(block)
        else:
            # raise Exception(colored("Block is invalid", "red"))
            print(colored("Block is invalid", "red"))

    def validate_block(self, block):
        if block == self._genesis:
            return True

        dup_state = self._state.copy()

        for leaf in block.leaves():
            if leaf.txn().from_address() is None or leaf.txn().from_address() not in dup_state:
                return False
            elif leaf.txn().from_address() is not None and leaf.txn().from_address() in dup_state:
                dup_state[leaf.txn().from_address()] = dup_state[leaf.txn().from_address()] - leaf.txn().amount()

        for key in dup_state:
            if dup_state[key] < 0:
                return False

        return True

    def validate_blockchain(self, blockchain):
        for block in blockchain.blocks():
            if blockchain.validate_block(block) == False:
                # print(colored("ERROR CAME FROM validate_block", "red"))
                # ipdb.set_trace()
                return False
            if block.validate_nonce(block.nonce()) == False:
                # print(colored("ERROR CAME FROM validate_nonce", "red"))
                # ipdb.set_trace()
                return False
            for leaf in block.leaves():
                if leaf.txn().validate_signature() == False:
                    # print(colored("ERROR CAME FROM validate_signature", "red"))
                    # ipdb.set_trace()
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
        if len(blockchain.blocks()) <= len(self._blocks):
            return False
        elif self.validate_blockchain(blockchain) is False:
            print(colored("FORK UNSUCCESSFUL: Blockchain is invalid...no fork will be executed", "red"))
            return False
        else:
            return self.switch_blockchain(blockchain)

    def switch_blockchain(self, blockchain):
        self._blocks = blockchain.blocks()
        self._state = {}
        self._genesis = self._blocks[0]
        map(lambda block: self.execute_txns(block), self._blocks)
        print(colored("FORK SUCCESSFUL: Blockchain was switched over to another longer chain", "green"))
        return True

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
        blockchain_two = BlockChain(100, satoshi_pubkey, satoshi_privkey)

        genesis_block = blockchain.blocks()[0]
        print(genesis_block.validate_nonce(genesis_block.nonce()))
        txn1 = Transaction(satoshi_pubkey, alice_pubkey, 15, satoshi_privkey)
        txn2 = Transaction(satoshi_pubkey, bob_pubkey, 15, satoshi_privkey)
        new_block = Block([txn1, txn2], genesis_block.hash)
        blockchain.append(new_block)
        blockchain_two.append(new_block)

        txn3 = Transaction(satoshi_pubkey, alice_pubkey, 15, satoshi_privkey)
        txn4 = Transaction(satoshi_pubkey, bob_pubkey, 15, satoshi_privkey)
        new_block_two = Block([txn3, txn4], new_block.hash)
        blockchain_two.append(new_block_two)

        blockchain.decide_fork(blockchain_two)
        ipdb.set_trace()
    except:
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        ipdb.post_mortem(tb)
