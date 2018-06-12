from datetime import datetime

import pytest

from pychain.block import Block
from pychain.blockchain import Blockchain
from pychain.config import PYCHAIN_PUBKEY
from pychain.transaction import Transaction


@pytest.fixture
def pc():
    return Blockchain()


@pytest.fixture
def trans1():
    return Transaction(PYCHAIN_PUBKEY, PYCHAIN_PUBKEY, "Test block #1", 10)


def test_block():
    index = 99999
    timestamp = datetime.now()
    trans = Transaction(PYCHAIN_PUBKEY, PYCHAIN_PUBKEY, "Test block", 1000)
    previous_hash = "test block hash"
    block = Block(index, timestamp, previous_hash)
    block + trans
    assert block.index == 99999
    assert isinstance(block.timestamp, datetime)
    assert isinstance(block.transactions, list)
    assert isinstance(block.transactions[0], Transaction)
    assert len(block) == 1
    assert block.transactions[0].validate is True
    assert block.previous_hash == "test block hash"
    assert len(block.hash) == 64
    with pytest.raises(ValueError):
        block.add(trans)


def test_blockchain(pc):
    assert isinstance(pc, Blockchain)
    assert len(pc.transactions) == 1
    assert pc.next_index == 1
    assert pc.last_block == pc.blockchain[0]
    assert pc.nodes == []
    assert pc.other_chains == []
    assert isinstance(pc.blockchain[0], Block)
    assert pc.blockchain[0].index == 0
    assert isinstance(pc.blockchain[0].transactions, list)
    assert isinstance(pc.blockchain[0].transactions[0], dict)
    assert pc.blockchain[0].transactions[0]["desc"] == "Genesis block"
    assert pc.blockchain[0].transactions[0]["data"] == 1000
    assert pc.blockchain[0].transactions[0]["from"] == PYCHAIN_PUBKEY
    assert pc.blockchain[0].transactions[0]["to"] == PYCHAIN_PUBKEY


def test_transaction(trans1):
    assert isinstance(trans1, Transaction)
    assert trans1.user_id == PYCHAIN_PUBKEY
    assert trans1.subject_id == PYCHAIN_PUBKEY
    assert trans1.desc == "Test block #1"
    assert trans1.payload == 10


def test_add_block(pc, trans1):
    pc.add_block(trans1)
    assert len(pc.blockchain) == 2
    assert isinstance(pc.blockchain[1], Block)


def test_validate_chain(pc, trans1):
    pc.add_block(trans1)
    trans2 = Transaction(PYCHAIN_PUBKEY, PYCHAIN_PUBKEY, "Test block #2", 5)
    pc.add_block(trans2)
    trans3 = Transaction(PYCHAIN_PUBKEY, PYCHAIN_PUBKEY, "Test block #3", 15)
    pc.add_block(trans3)
    assert pc.validate_chain() is True
