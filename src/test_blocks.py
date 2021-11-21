import hashlib

import pytest

import blocks


@pytest.fixture
def reward() -> blocks.Transaction:
    """ """
    return blocks.Transaction(
        reference_hash=blocks.REWARD_HASH, sender=blocks.REWARD_SENDER, receiver=7000
    )


@pytest.fixture
def blockchain_with_1_block() -> blocks.Blockchain:
    """ """
    block = blocks.init_genesis_block()
    block_hash = hashlib.sha256(hashlib.sha256(block.header.encode()).digest()).digest()

    return blocks.Blockchain(chain=[block_hash], blocks={block_hash: block})


@pytest.fixture
def blockchain_with_2_blocks(reward) -> blocks.Blockchain:
    """ """
    block = blocks.init_genesis_block()
    block_hash = hashlib.sha256(hashlib.sha256(block.header.encode()).digest()).digest()

    blockchain = blocks.Blockchain(chain=[block_hash], blocks={block_hash: block})

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

    return blockchain


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
        bytes.hex(block_hash)
        == "00001ff58495c3dc2a1aaa69ebca4e9b3e05e63e5a319fb73bcdccbcdbba1e72"
    )
    assert (
        bytes.hex(header.encode())
        == "000000000000000000000000000000000000000000000000000000000000000000616f8ae000000000000000000000000000000000000000000000000000000000000114a6"
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
        bytes.hex(block_hash)
        == "000071e6ff5b358e57339b42d45b20acc0f112c218fa435b3ffa8f239b777347"
    )
    assert (
        bytes.hex(header.encode())
        == "0000001ff58495c3dc2a1aaa69ebca4e9b3e05e63e5a319fb73bcdccbcdbba1e72616f8d38000000000000000000000000000000000000000000000000000000000000e590"
    )


def test_validate_blockchain(reward, blockchain_with_1_block, blockchain_with_2_blocks):
    """ """
    blockchain = blockchain_with_1_block
    assert blocks.validate_blockchain(blockchain)

    blockchain = blockchain_with_2_blocks
    assert blocks.validate_blockchain(blockchain)

    _, _, _, header = blocks.run_proof_of_work(
        (0).to_bytes(32, byteorder="big"), 1634701200, 95000, 1000
    )

    block = blocks.Block(header=header, transactions=[reward])
    block_hash = hashlib.sha256(hashlib.sha256(header.encode()).digest()).digest()

    blockchain.chain.append(block_hash)
    blockchain.blocks[block_hash] = block

    assert not blocks.validate_blockchain(blockchain)


def test_replace_blockchain(blockchain_with_1_block, blockchain_with_2_blocks):
    """ """
    assert blocks.replace_blockchain(blockchain_with_1_block, blockchain_with_2_blocks)
    assert not blocks.replace_blockchain(
        blockchain_with_1_block, blockchain_with_1_block
    )


def test_decode_message():
    """ """
    block = blocks.init_genesis_block()
    block_hash = hashlib.sha256(hashlib.sha256(block.header.encode()).digest()).digest()
    blockchain = blocks.Blockchain(chain=[block_hash], blocks={block_hash: block})
    blockchain_bytes = blockchain.encode()

    assert blocks.decode_message(blockchain_bytes).encode() == blockchain_bytes
