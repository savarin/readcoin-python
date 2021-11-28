from typing import Dict
import hashlib

import pytest

import blocks
import crypto
import transactions as transacts


@pytest.fixture
def wallets() -> Dict[int, crypto.Wallet]:
    """ """
    return crypto.load_demo_wallets()


@pytest.fixture
def reward(wallets) -> transacts.Transaction:
    """ """
    return transacts.init_reward(wallets[7000].address)


@pytest.fixture
def transfer(wallets, reward) -> transacts.Transaction:
    """ """
    reference_hash = hashlib.sha256(reward.encode()).digest()
    sender = wallets[7000].address
    receiver = wallets[8000].address
    signature = bytes.fromhex(
        "304402205393ece4549b926f429c4173b7d6e8f4da4222d63adc23bbc7ce36321c4e626c02205828f91c27f96de27224affb468338f5eb34cbdc9521690964689fb68a5ea213"
    )

    return transacts.Transaction(
        reference_hash=reference_hash,
        sender=sender,
        receiver=receiver,
        signature=signature,
    )


@pytest.fixture
def merkle_root_with_1_transaction(reward) -> transacts.Hash:
    """ """
    merkle_tree = transacts.init_merkle_tree([hashlib.sha256(reward.encode()).digest()])

    assert merkle_tree is not None
    return merkle_tree.tree_hash


@pytest.fixture
def merkle_root_with_2_transactions(reward, transfer) -> transacts.Hash:
    """ """
    merkle_tree = transacts.init_merkle_tree(
        [
            hashlib.sha256(reward.encode()).digest(),
            hashlib.sha256(transfer.encode()).digest(),
        ]
    )

    assert merkle_tree is not None
    return merkle_tree.tree_hash


@pytest.fixture
def blockchain_with_1_block(wallets) -> blocks.Blockchain:
    """ """
    return blocks.init_blockchain(wallets[7000].address)


@pytest.fixture
def blockchain_with_2_blocks(
    wallets, reward, transfer, merkle_root_with_2_transactions
) -> blocks.Blockchain:
    """ """
    blockchain = blocks.init_blockchain(wallets[7000].address)

    header = blocks.Header(
        version=blocks.VERSION,
        previous_hash=blockchain.chain[0],
        merkle_root=merkle_root_with_2_transactions,
        timestamp=1634700600,
        nonce=38997,
    )

    block = blocks.Block(header=header, transactions=[reward, transfer])
    block_hash = hashlib.sha256(hashlib.sha256(header.encode()).digest()).digest()

    blockchain.chain.append(block_hash)
    blockchain.blocks[block_hash] = block

    return blockchain


def test_proof_of_work(merkle_root_with_1_transaction, merkle_root_with_2_transactions):
    """ """
    previous_hash = (0).to_bytes(32, byteorder="big")
    timestamp = 1634700000

    is_new_block, nonce, block_hash, header = blocks.run_proof_of_work(
        previous_hash, merkle_root_with_1_transaction, timestamp, 0, 1000
    )

    assert not is_new_block
    assert nonce == 1000
    assert block_hash is None
    assert header is None

    is_new_block, nonce, block_hash, header = blocks.run_proof_of_work(
        previous_hash, merkle_root_with_1_transaction, timestamp, 48000, 1000
    )

    assert is_new_block
    assert nonce == 48705
    assert (
        bytes.hex(block_hash)
        == "0000704291eb05b64b2d0fbfa5be0e5d8176bf97c30ee9be08db19846aade9ce"
    )
    assert (
        bytes.hex(header.encode())
        == "02000000000000000000000000000000000000000000000000000000000000000078ab8e2fe28bb3faf504ef7684e73d999359284f80213a0de57d0dd4bba36783616f8ae0000000000000000000000000000000000000000000000000000000000000be41"
    )

    previous_hash = block_hash
    timestamp = 1634700600

    is_new_block, nonce, block_hash, header = blocks.run_proof_of_work(
        previous_hash, merkle_root_with_2_transactions, timestamp, 0, 1000
    )

    assert not is_new_block
    assert nonce == 1000
    assert block_hash is None
    assert header is None

    is_new_block, nonce, block_hash, header = blocks.run_proof_of_work(
        previous_hash, merkle_root_with_2_transactions, timestamp, 11000, 1000
    )

    assert is_new_block
    assert nonce == 11293
    assert (
        bytes.hex(block_hash)
        == "000021277969446ebde2ddaaf35a88cbae02a4eb8e303ab936d28d27d4396ee8"
    )
    assert (
        bytes.hex(header.encode())
        == "020000704291eb05b64b2d0fbfa5be0e5d8176bf97c30ee9be08db19846aade9ce00f39e382b27783998f28de664c436e7afbac7a87c3041ea156150a50d6c47fe616f8d380000000000000000000000000000000000000000000000000000000000002c1d"
    )


def test_decode_blockchain(blockchain_with_1_block, blockchain_with_2_blocks):
    """ """
    blockchain_bytes = blockchain_with_1_block.encode()
    assert blocks.decode_blockchain(blockchain_bytes).encode() == blockchain_bytes

    blockchain_bytes = blockchain_with_2_blocks.encode()
    assert blocks.decode_blockchain(blockchain_bytes).encode() == blockchain_bytes
