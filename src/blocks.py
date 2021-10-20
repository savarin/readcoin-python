from typing import Optional, Tuple
import hashlib


VERSION: int = 0


def init_block_header(previous_hash: bytes, timestamp: int, nonce: int) -> bytes:
    """ """
    return (
        VERSION.to_bytes(1, byteorder="big")
        + previous_hash
        + timestamp.to_bytes(4, byteorder="big")
        + nonce.to_bytes(32, byteorder="big")
    )


def init_transactions(node_port: int):
    """ """
    sender = (0).to_bytes(2, byteorder="big")
    receiver = node_port.to_bytes(2, byteorder="big")

    transaction_counter = 1
    transactions = sender + receiver

    return transaction_counter, transactions


def init_block(
    block_header: bytes, transaction_counter: int, transactions: bytes
) -> bytes:
    """ """
    block_size = 1 + 41 + 1 + len(transactions)

    return (
        block_size.to_bytes(1, byteorder="big")
        + block_header
        + transaction_counter.to_bytes(1, byteorder="big")
        + transactions
    )


def init_genesis_block():
    """ """
    previous_hash = (0).to_bytes(32, byteorder="big")
    timestamp = 1634700000
    nonce = 70822

    block_header = init_block_header(previous_hash, timestamp, nonce)
    guess = hashlib.sha256(hashlib.sha256(block_header).digest())

    transaction_counter, transactions = init_transactions(7000)
    block = init_block(block_header, transaction_counter, transactions)

    return block_header, guess.digest(), block


def solve_block_header(
    previous_hash: bytes,
    timestamp: int,
    nonce: int = 0,
    iterations: Optional[int] = None,
) -> Tuple[bool, Optional[bytes], Optional[bytes]]:
    """Find nonce that makes the first 4 bytes of twice-hashed header all zeroes. Maximum number of
    iterations can be specified."""
    counter = 0

    while True:
        block_header = init_block_header(previous_hash, timestamp, nonce)
        guess = hashlib.sha256(hashlib.sha256(block_header).digest())

        if guess.hexdigest()[:4] == "0000":
            break

        if iterations is not None and counter == iterations:
            return False, None, None

        nonce += 1
        counter += 1

    return True, block_header, guess.digest()
