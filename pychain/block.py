import hashlib

from pychain.config import PYCHAIN_PUBKEY

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
