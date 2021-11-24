from typing import DefaultDict, List, Optional, Tuple
import collections
import dataclasses
import hashlib

import blocks
import transactions as transacts


Accounts = DefaultDict[int, List[blocks.Hash]]


@dataclasses.dataclass
class Balance:
    """ """

    latest_hash: blocks.Hash
    accounts: Accounts


def update_accounts(accounts: Accounts, block: blocks.Block) -> Accounts:
    """ """
    for transaction in block.transactions:
        if transaction.sender != 0:
            accounts[transaction.sender].remove(transaction.reference_hash)

        reference_hash = hashlib.sha256(transaction.encode()).digest()
        accounts[transaction.receiver].append(reference_hash)

    return accounts


def init_balance(blockchain: blocks.Blockchain) -> Balance:
    """ """
    accounts: Accounts = collections.defaultdict(list)

    for block_hash in blockchain.chain:
        block = blockchain.blocks[block_hash]
        accounts = update_accounts(accounts, block)

    return Balance(latest_hash=block_hash, accounts=accounts)


def update_balance(balance: Balance, block: blocks.Block) -> Balance:
    """ """
    block_hash = hashlib.sha256(hashlib.sha256(block.header.encode()).digest()).digest()
    balance.latest_hash = block_hash

    balance.accounts = update_accounts(balance.accounts, block)

    return balance


def init_transfer(
    balance: Balance, sender: int, receiver: int
) -> Tuple[Optional[Balance], Optional[transacts.Transaction]]:
    """ """
    if sender not in balance.accounts or len(balance.accounts[sender]) == 0:
        return None, None

    reference_hash = balance.accounts[sender].pop(0)
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

    if is_zero_reference != is_zero_sender:
        return False

    if sender not in balance.accounts or len(balance.accounts[sender]) == 0:
        return False

    return transaction.reference_hash in balance.accounts[transaction.sender]
