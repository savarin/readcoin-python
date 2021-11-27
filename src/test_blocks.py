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
    signature = "30460221008256ee455eff519f35212f3b78e97b10c20cfc3c3f695e215b048af86a7ddee2022100a80931210346355a6ed475dc402a091b4061061442b28445b0d9bdc78f333aee".encode()

    return transacts.Transaction(
        reference_hash=reference_hash, sender=sender, receiver=receiver, signature=signature
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
        nonce=22025,
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
        previous_hash, merkle_root_with_1_transaction, timestamp, 82000, 1000
    )

    assert is_new_block
    assert nonce == 82822
    assert (
        bytes.hex(block_hash)
        == "0000a0939d2ea8133efef4576aceac9e89b66298ecafce0615d1de4dc06db7c8"
    )
    assert (
        bytes.hex(header.encode())
        == "00000000000000000000000000000000000000000000000000000000000000000078ab8e2fe28bb3faf504ef7684e73d999359284f80213a0de57d0dd4bba36783616f8ae00000000000000000000000000000000000000000000000000000000000014386"
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
        previous_hash, merkle_root_with_2_transactions, timestamp, 117000, 1000
    )

    assert is_new_block
    assert nonce == 117392
    assert (
        bytes.hex(block_hash)
        == "000028924a3ee6e9d76537d78e1adef30b511f6ee549061c83800ef8e80df3f4"
    )
    assert (
        bytes.hex(header.encode())
        == "000000a0939d2ea8133efef4576aceac9e89b66298ecafce0615d1de4dc06db7c842dc8d05bb6998db8e14a3233d3aad9fa536c8add09d5005a37d44e5b5521a2c616f8d38000000000000000000000000000000000000000000000000000000000001ca90"
    )


def test_decode_blockchain(blockchain_with_1_block):
    """ """
    blockchain_bytes = blockchain_with_1_block.encode()

    assert blocks.decode_blockchain(blockchain_bytes).encode() == blockchain_bytes
