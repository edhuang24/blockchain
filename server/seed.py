import pickle
import dill
import codecs
import pdb
from blockchain import *

alice_key = RSA.generate(1024, Random.new().read)
alice_privkey = alice_key.exportKey()
alice_pubkey = alice_key.publickey().exportKey()

bob_key = RSA.generate(1024, Random.new().read)
bob_privkey = bob_key.exportKey()
bob_pubkey = bob_key.publickey().exportKey()

satoshi_key = RSA.generate(1024, Random.new().read)
satoshi_privkey = satoshi_key.exportKey()
satoshi_pubkey = satoshi_key.publickey().exportKey()

txn1 = Transaction(alice_pubkey, bob_pubkey, 10, alice_privkey)
# print(txn1.validate_signature())

blockchain = BlockChain(50000, satoshi_pubkey, satoshi_privkey)
genesis_block = blockchain.blocks()[0]
print(genesis_block.validate_nonce(genesis_block.nonce()))

txn2 = Transaction(satoshi_pubkey, alice_pubkey, 15, satoshi_privkey)
txn3 = Transaction(satoshi_pubkey, bob_pubkey, 15, satoshi_privkey)
new_block = Block([txn1, txn2], genesis_block.hash)

blockchain.append(new_block)

bytes = pickle.dumps(blockchain)
encoded = codecs.encode(bytes, "base64")
# decoded = codecs.decode(encoded, "base64")

with open("seed.txt", "w") as new_file:
    new_file.write(encoded)
