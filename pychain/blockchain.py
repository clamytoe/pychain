import json
from datetime import datetime

import requests

from pychain.block import Block
from pychain.config import PYCHAIN_PUBKEY
from pychain.transaction import Transaction


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
            if block.transactions[0]["desc"] == "Genesis block":
                previous_block = block
            else:
                # check that the hash of the current block is valid
                if block.previous_hash != previous_block.hash:
                    return False
                # set the currently checked block as the previous one
                previous_block = block
        return True

    @property
    def get_blocks(self):
        block_list = ""

        for block in self.blockchain:
            assembled = json.dumps(
                {
                    "index": str(block.index),
                    "timestamp": str(block.timestamp),
                    "data": str(block.data),
                    "hash": block.hash,
                }
            )
            block_list += assembled

        return block_list

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
