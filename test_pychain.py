import pytest
from pychain import Block, Blockchain, Transaction
from config import PYCHAIN_PUBKEY


@pytest.fixture
def pc():
    return Blockchain()


@pytest.fixture
def trans1():
    return Transaction(PYCHAIN_PUBKEY, PYCHAIN_PUBKEY, "Test block #1", 10)


def test_blockchain(pc):
    assert isinstance(pc, Blockchain)
    assert len(pc.transactions) == 1
    assert pc.next_index == 1
    assert pc.last_block == pc.blockchain[0]
    assert pc.nodes == []
    assert pc.other_chains == []
    assert isinstance(pc.blockchain[0], Block)
    assert pc.blockchain[0].index == 0
    assert isinstance(pc.blockchain[0].data, dict)
    assert pc.blockchain[0].data["proof-of-work"] == 9
    assert pc.blockchain[0].data["transaction"]["comment"] == "Genesis block"
    assert pc.blockchain[0].data["transaction"]["amount"] == 1000
    assert pc.blockchain[0].data["transaction"]["from"] == PYCHAIN_PUBKEY
    assert pc.blockchain[0].data["transaction"]["to"] == PYCHAIN_PUBKEY


def test_transaction(trans1):
    assert isinstance(trans1, Transaction)
    assert trans1.sender == PYCHAIN_PUBKEY
    assert trans1.receiver == PYCHAIN_PUBKEY
    assert trans1.comment == "Test block #1"
    assert trans1.amount == 10


def test_add_block(pc, trans1):
    pc.add_block(pc.proof_of_work, trans1)
    assert len(pc.blockchain) == 2
    assert isinstance(pc.blockchain[1], Block)


def test_validate_chain(pc, trans1):
    pc.add_block(pc.proof_of_work, trans1)
    trans2 = Transaction(PYCHAIN_PUBKEY, PYCHAIN_PUBKEY, "Test block #2", 5)
    pc.add_block(pc.proof_of_work, trans2)
    trans3 = Transaction(PYCHAIN_PUBKEY, PYCHAIN_PUBKEY, "Test block #3", 15)
    pc.add_block(pc.proof_of_work, trans3)
    assert pc.validate_chain() == True
