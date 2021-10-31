import binascii
import hashlib

import blocks


def test_proof_of_work():
    """ """
    previous_hash = (0).to_bytes(32, byteorder="big")
    timestamp = 1634700000

    is_new_block, nonce, block_hash, header = blocks.run_proof_of_work(
        previous_hash, timestamp, 0, 1000
    )

    assert not is_new_block
    assert nonce == 1000
    assert block_hash is None
    assert header is None

    is_new_block, nonce, block_hash, header = blocks.run_proof_of_work(
        previous_hash, timestamp, 70000, 1000
    )

    assert is_new_block
    assert nonce == 70822
    assert (
        binascii.hexlify(block_hash)
        == b"00001ff58495c3dc2a1aaa69ebca4e9b3e05e63e5a319fb73bcdccbcdbba1e72"
    )
    assert (
        binascii.hexlify(header.encode())
        == b"000000000000000000000000000000000000000000000000000000000000000000616f8ae000000000000000000000000000000000000000000000000000000000000114a6"
    )

    previous_hash = block_hash
    timestamp = 1634700600

    is_new_block, nonce, block_hash, header = blocks.run_proof_of_work(
        previous_hash, timestamp, 0, 1000
    )

    assert not is_new_block
    assert nonce == 1000
    assert block_hash is None
    assert header is None

    is_new_block, nonce, block_hash, header = blocks.run_proof_of_work(
        previous_hash, timestamp, 58000, 1000
    )

    assert is_new_block
    assert nonce == 58768
    assert (
        binascii.hexlify(block_hash)
        == b"000071e6ff5b358e57339b42d45b20acc0f112c218fa435b3ffa8f239b777347"
    )
    assert (
        binascii.hexlify(header.encode())
        == b"0000001ff58495c3dc2a1aaa69ebca4e9b3e05e63e5a319fb73bcdccbcdbba1e72616f8d38000000000000000000000000000000000000000000000000000000000000e590"
    )


def test_validate_blockchain():
    """ """
    block = blocks.init_genesis_block()
    block_hash = hashlib.sha256(hashlib.sha256(block.header.encode()).digest()).digest()
    blockchain = blocks.Blockchain(chain=[block_hash], blocks={block_hash: block})

    assert blocks.validate_blockchain(blockchain)

    reward = blocks.Transaction(
        reference_hash=blocks.REWARD_HASH, sender=blocks.REWARD_SENDER, receiver=7000
    )

    header = blocks.Header(
        version=blocks.VERSION,
        previous_hash=block_hash,
        timestamp=1634700600,
        nonce=58768,
    )
    block = blocks.Block(header=header, transactions=[reward])

    block_hash = hashlib.sha256(hashlib.sha256(header.encode()).digest()).digest()
    blockchain.chain.append(block_hash)
    blockchain.blocks[block_hash] = block

    assert blocks.validate_blockchain(blockchain)

    _, _, _, header = blocks.run_proof_of_work(
        (0).to_bytes(32, byteorder="big"), 1634701200, 95000, 1000
    )
    block = blocks.Block(header=header, transactions=[reward])

    block_hash = hashlib.sha256(hashlib.sha256(header.encode()).digest()).digest()
    blockchain.chain.append(block_hash)
    blockchain.blocks[block_hash] = block

    assert not blocks.validate_blockchain(blockchain)


def test_validate_transactions():
    """ """
    block = blocks.init_genesis_block()
    block_hash = hashlib.sha256(hashlib.sha256(block.header.encode()).digest()).digest()
    blockchain = blocks.Blockchain(chain=[block_hash], blocks={block_hash: block})

    reference_hash = block_hash

    assert blocks.validate_transaction(blockchain, reference_hash, 7000)

    reward = blocks.Transaction(
        reference_hash=blocks.REWARD_HASH, sender=blocks.REWARD_SENDER, receiver=7000
    )
    transaction = blocks.Transaction(
        reference_hash=block_hash, sender=7000, receiver=8000
    )

    header = blocks.Header(
        version=blocks.VERSION,
        previous_hash=block_hash,
        timestamp=1634700600,
        nonce=58768,
    )
    block = blocks.Block(header=header, transactions=[reward, transaction])

    block_hash = hashlib.sha256(hashlib.sha256(header.encode()).digest()).digest()
    blockchain.chain.append(block_hash)
    blockchain.blocks[block_hash] = block

    assert not blocks.validate_transaction(blockchain, reference_hash, 7000)


def test_decode_message():
    """ """
    block = blocks.init_genesis_block()
    block_hash = hashlib.sha256(hashlib.sha256(block.header.encode()).digest()).digest()
    blockchain = blocks.Blockchain(chain=[block_hash], blocks={block_hash: block})
    blockchain_bytes = blockchain.encode()

    assert blocks.decode_message(blockchain_bytes).encode() == blockchain_bytes
