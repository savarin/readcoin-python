VERSION: int = 0


def init_block_header(prev_hash: bytes, timestamp: int, nonce: int) -> bytes:
    """ """
    return (
        VERSION.to_bytes(1, byteorder="big")
        + prev_hash
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
