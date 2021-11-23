from typing import DefaultDict, List, Optional, Tuple
import collections
import dataclasses
import hashlib

import blocks
import transactions as transacts


Account = DefaultDict[int, List[blocks.Hash]]


@dataclasses.dataclass
class Balance:
    """ """

    latest_hash: blocks.Hash
    account: Account


def update_account_with_block(
    account: Account, blockchain: blocks.Blockchain, block_hash: blocks.Hash
) -> Account:
    """ """
    block = blockchain.blocks[block_hash]

    for transaction in block.transactions:
        if transaction.sender != 0:
            account[transaction.sender].remove(transaction.reference_hash)

        reference_hash = hashlib.sha256(transaction.encode()).digest()
        account[transaction.receiver].append(reference_hash)

    return account


def init_balance(blockchain: blocks.Blockchain) -> Balance:
    """ """
    account: Account = collections.defaultdict(list)

    for block_hash in blockchain.chain:
        account = update_account_with_block(account, blockchain, block_hash)

    return Balance(latest_hash=block_hash, account=account)


def update_balance_with_blockchain(
    balance: Balance, blockchain: blocks.Blockchain
) -> Tuple[bool, Optional[Balance]]:
    """ """
    if balance.latest_hash not in blockchain.chain:
        return False, None

    hash_index = blockchain.chain.index(balance.latest_hash)

    for block_hash in blockchain.chain[hash_index + 1 :]:
        balance.account = update_account_with_block(
            balance.account, blockchain, block_hash
        )

    return True, balance


def init_transfer(
    balance: Balance, sender: int, receiver: int
) -> Tuple[Optional[Balance], Optional[transacts.Transaction]]:
    """ """
    if sender not in balance.account or len(balance.account[sender]) == 0:
        return None, None

    reference_hash = balance.account[sender].pop(0)
    transaction = transacts.Transaction(
        reference_hash=reference_hash, sender=sender, receiver=receiver
    )

    return balance, transaction


def validate_transaction(balance: Balance, transaction: transacts.Transaction) -> bool:
    """ """
    sender = transaction.sender

    is_zero_reference = transaction.reference_hash == blocks.REWARD_HASH
    is_zero_sender = sender == 0

    if is_zero_reference and is_zero_sender:
        return True

    elif is_zero_reference != is_zero_sender:
        return False

    if sender not in balance.account or len(balance.account[sender]) == 0:
        return False

    return transaction.reference_hash in balance.account[transaction.sender]
