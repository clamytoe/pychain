import hashlib
import json
from datetime import datetime

import requests

from config import PYCHAIN_PUBKEY

AUTH_SIZE = 32
REQUIRE_POW = False


class Block:
    def __init__(self, index, timestamp, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.transactions = []

    def __add__(self, transaction):
        if len(self) > 0:
            for trans in self.transactions:
                if trans.trans_id == transaction.trans_id:
                    raise ValueError(
                        f"Transaction #{transaction.trans_id} already exists."
                    )
            self.transactions.append(transaction)
        else:
            self.transactions = [transaction]

    def __len__(self):
        return len(self.transactions)

    def add(self, transaction):
        self.__add__(transaction)

    @property
    def hash(self):
        key = PYCHAIN_PUBKEY.encode()
        h = hashlib.blake2b(digest_size=AUTH_SIZE, key=key)
        payload = f"{self.index},{self.timestamp},{self.transactions}," \
                  f"{self.previous_hash} "
        h.update(payload.encode())

        return h.hexdigest()

    def __repr__(self):
        return f"Block({self.index}, {self.timestamp}, {self.transactions}, "\
               f"{self.previous_hash})"


class Blockchain:
    def __init__(self, blockchain=None, nodes=None, transactions=None):
        self.blockchain = blockchain if blockchain else []
        self.nodes = nodes if nodes else []
        self.transactions = transactions if transactions else []

        self.create_genesis_block()

    def __len__(self):
        return len(self.blockchain)

    def add_block(self, transaction):
        valid = transaction.validate
        if valid:
            trans = json.loads(transaction.trans)
            index = 0 if len(self.blockchain) == 0 else self.next_index
            prev_hash = 0 if len(self.blockchain) == 0 else self.previous_hash
            block = Block(index, datetime.now(), prev_hash)
            block.add(trans)
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
            trans = Transaction(PYCHAIN_PUBKEY, PYCHAIN_PUBKEY,
                                "Genesis block", 1000)
            self.add_block(trans)

    def validate_chain(self):
        previous_block = None
        for block in self.blockchain:
            print(f"CHECKING BLOCK #{block.index}: [{len(block)}]")
            print(f"BLOCK #{block.index}: {block.hash}")
            print(f"PBLOCK: {block.previous_hash}")
            if block.transactions[0]["desc"] == "Genesis block":
                print("Found Genesis Block")
                print(f"GENESIS #{block.index}: {block.hash}")
                previous_block = block
            else:
                # check that the hash of the current block is valid
                print(f"Previous hash: {previous_block.hash}")
                print(f"Block #{block.index} has: {block.hash}")
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
                requests.get(url + "/blocks").content) for url in self.nodes
        ]
        return nodes_

    @property
    def previous_hash(self):
        return self.last_block.hash


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

    @property
    def validate(self):
        trans = json.loads(self.trans)
        return (
            True
            if (
                trans["id"]
                and trans["from"]
                and trans["to"]
                and trans["desc"]
                and trans["data"]
            )
            else False
        )