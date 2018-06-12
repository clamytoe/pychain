from datetime import datetime
import hashlib
import json
import requests

from config import PYCHAIN_PUBKEY

AUTH_SIZE = 32
REQUIRE_POW = False


class Block:

    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        key = PYCHAIN_PUBKEY.encode()
        h = hashlib.blake2b(digest_size=AUTH_SIZE, key=key)
        payload = f"{self.index},{self.timestamp},{self.data}," \
                  f"{self.previous_hash} "
        h.update(payload.encode())

        return h.hexdigest()

    def __repr__(self):
        return f"Block({self.index}, {self.timestamp}, {self.data}, " \
               f"{self.previous_hash})"


class Blockchain:

    def __init__(self, blockchain=None, nodes=None, transactions=None):
        self.blockchain = blockchain if blockchain else []
        self.nodes = nodes if nodes else []
        self.transactions = transactions if transactions else []

        self.create_genesis_block()

    def __len__(self):
        return len(self.blockchain)

    def add_block(self, proof, transaction):
        valid = transaction.validate()
        if valid:
            trans = json.loads(transaction.trans)
            data = {"proof-of-work": proof, "transaction": trans}
            index = 0 if len(self.blockchain) == 0 else self.next_index
            prev_hash = 0 if len(self.blockchain) == 0 else self.previous_hash
            block = Block(index, datetime.now(), data, prev_hash)
            self.blockchain.append(block)
            self.transactions.append(trans)

    def add_node(self, url):
        if url not in self.nodes:
            self.nodes.append(url)

    def consensus(self):
        # Get the blocks from other nodes
        other_chains = self.other_chains
        longest_chain = self.blockchain

        for chain in other_chains:
            if len(longest_chain) < len(chain):
                longest_chain = chain

        self.blockchain = longest_chain

    def create_genesis_block(self):
        # Manually construct a block with
        # index zero and arbitrary previous hash
        if not self.blockchain:
            proof = self.proof_of_work
            trans = Transaction(
                PYCHAIN_PUBKEY,
                PYCHAIN_PUBKEY,
                "Genesis block",
                1000,
            )
            self.add_block(proof, trans)

    def validate_chain(self):
        for block in self.blockchain:
            # skip over genesis block but set it as the previous block
            if block.data["transaction"]["comment"] == "Genesis block":
                previous_block = block
                continue
            else:
                # check that the hash of the current block is valid
                if block.hash != block.hash_block():
                    return False
                # check that the previous_block's hash is the same as the hash
                # entry of this block
                if block.previous_hash != previous_block.hash:
                    return False
            # set the currently checked block as the previous one
            previous_block = block
        return True

    @property
    def get_blocks(self):
        blocklist = ""

        for block in self.blockchain:
            assembled = json.dumps(
                {
                    "index": str(block.index),
                    "timestamp": str(block.timestamp),
                    "data": str(block.data),
                    "hash": block.hash,
                }
            )
            blocklist += assembled

        return blocklist

    @property
    def last_block(self):
        return self.blockchain[-1]

    @property
    def next_index(self):
        return self.last_block.index + 1

    @property
    def last_proof(self):
        return self.last_block.data["proof-of-work"]

    @property
    def other_chains(self):
        nodes_ = [
            json.loads(
                requests.get(url + "/blocks").content
            ) for url in self.nodes
        ]
        return nodes_

    @property
    def previous_hash(self):
        return self.last_block.hash

    @property
    def proof_of_work(self):
        return self.last_proof if REQUIRE_POW else 9


class Transaction:

    def __init__(self, user_id, subject_id, desc, payload):
        self.trans_id = datetime.now().toordinal()
        self.user_id = user_id
        self.subject_id = subject_id
        self.desc = desc
        self.payload = payload

    @property
    def trans(self):
        return json.dumps(
            {
                "id": self.trans_id,
                "from": self.user_id,
                "to": self.subject_id,
                "desc": self.desc,
                "data": self.payload,
            }
        )

    def validate(self):
        trans = json.loads(self.trans)
        return True if (
            trans["id"] and
            trans["from"] and
            trans["to"] and
            trans["desc"] and
            trans["data"]
        ) else False
