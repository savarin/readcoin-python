import hashlib

import pytest

import balances
import blocks
import transactions as transacts


@pytest.fixture
def reward() -> transacts.Transaction:
    """ """
    return transacts.Transaction(
        reference_hash=blocks.REWARD_HASH, sender=blocks.REWARD_SENDER, receiver=7000
    )


@pytest.fixture
def transfer(reward) -> transacts.Transaction:
    """ """
    reference_hash = hashlib.sha256(reward.encode()).digest()

    return transacts.Transaction(
        reference_hash=reference_hash, sender=7000, receiver=8000
    )


@pytest.fixture
def merkle_root_with_1_transaction(reward) -> blocks.Hash:
    """ """
    merkle_tree = transacts.init_merkle_tree([hashlib.sha256(reward.encode()).digest()])

    assert merkle_tree is not None
    return merkle_tree.tree_hash


@pytest.fixture
def merkle_root_with_2_transactions(reward, transfer) -> blocks.Hash:
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
def blockchain_with_1_block() -> blocks.Blockchain:
    """ """
    block = blocks.init_genesis_block()
    block_hash = hashlib.sha256(hashlib.sha256(block.header.encode()).digest()).digest()

    return blocks.Blockchain(chain=[block_hash], blocks={block_hash: block})


@pytest.fixture
def blockchain_with_2_blocks(
    reward, transfer, merkle_root_with_2_transactions
) -> blocks.Blockchain:
    """ """
    block = blocks.init_genesis_block()
    block_hash = hashlib.sha256(hashlib.sha256(block.header.encode()).digest()).digest()

    blockchain = blocks.Blockchain(chain=[block_hash], blocks={block_hash: block})

    header = blocks.Header(
        version=blocks.VERSION,
        previous_hash=block_hash,
        merkle_root=merkle_root_with_2_transactions,
        timestamp=1634700600,
        nonce=22025,
    )

    block = blocks.Block(header=header, transactions=[reward, transfer])
    block_hash = hashlib.sha256(hashlib.sha256(header.encode()).digest()).digest()

    blockchain.chain.append(block_hash)
    blockchain.blocks[block_hash] = block

    return blockchain


def test_init_balance(blockchain_with_1_block, blockchain_with_2_blocks):
    """ """
    balance = balances.init_balance(blockchain_with_1_block)

    assert (
        bytes.hex(balance.latest_hash)
        == "0000e07d18285944711e785cfa7aa96443ddc9a4dfacce935d3bbc9793181ad6"
    )
    assert len(balance.accounts) == 1

    assert len(balance.accounts[7000]) == 1
    assert (
        bytes.hex(balance.accounts[7000][0])
        == "281d8712b36b4365bd09fe91de46e78b69d5d4ecf078252eb35b2cbbb24ba057"
    )

    block_hash = blockchain_with_2_blocks.chain.pop()
    block = blockchain_with_2_blocks.blocks[block_hash]
    balance = balances.update_balance(balance, block)

    assert (
        bytes.hex(balance.latest_hash)
        == "00005b938d4fcaa18d0ccc4792100c5bcea26e0b56faec2334c8ea9d530c527e"
    )
    assert len(balance.accounts) == 2

    assert len(balance.accounts[7000]) == 1
    assert (
        bytes.hex(balance.accounts[7000][0])
        == "281d8712b36b4365bd09fe91de46e78b69d5d4ecf078252eb35b2cbbb24ba057"
    )

    assert len(balance.accounts[8000]) == 1
    assert (
        bytes.hex(balance.accounts[8000][0])
        == "9120067e60810ab80b5815a1faba23a5a00469a51c3e570090e36b01904b2de7"
    )


def test_init_transfer(blockchain_with_2_blocks):
    """ """
    balance = balances.init_balance(blockchain_with_2_blocks)
    reference_hash = balance.accounts[7000][0]

    _, transfer = balances.init_transfer(balance, 7000, 8000)

    assert transfer == transacts.Transaction(
        reference_hash=reference_hash, sender=7000, receiver=8000
    )


def test_validate_transaction(reward, transfer, blockchain_with_2_blocks):
    """ """
    pre_transfer_balance = balances.init_balance(blockchain_with_2_blocks)
    assert balances.validate_transaction(pre_transfer_balance, reward)
    assert balances.validate_transaction(pre_transfer_balance, transfer)

    post_transfer_balance, _ = balances.init_transfer(pre_transfer_balance, 7000, 8000)
    assert not balances.validate_transaction(post_transfer_balance, transfer)

    assert id(pre_transfer_balance) == id(post_transfer_balance)
