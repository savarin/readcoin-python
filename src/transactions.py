from typing import List, Optional, Tuple
import dataclasses
import hashlib


Hash = bytes


HASH_SIZE: int = 32
SIGNATURE_SIZE: int = 72
TRANSACTION_SIZE: int = 168  # i.e. 3 * 32 + 72

REWARD_HASH: bytes = (0).to_bytes(HASH_SIZE, byteorder="big")
REWARD_SENDER: bytes = (0).to_bytes(HASH_SIZE, byteorder="big")
REWARD_SIGNATURE: bytes = (0).to_bytes(SIGNATURE_SIZE, byteorder="big")


@dataclasses.dataclass
class Transaction:
    """ """

    reference_hash: Hash
    sender: Hash
    receiver: Hash
    signature: bytes

    def encode(self):
        """ """
        return self.reference_hash + self.sender + self.receiver + self.signature


def decode_transaction(transaction_bytes: bytes) -> Transaction:
    """ """
    reference_hash = transaction_bytes[:HASH_SIZE]
    sender = transaction_bytes[HASH_SIZE : 2 * HASH_SIZE]
    receiver = transaction_bytes[2 * HASH_SIZE : 3 * HASH_SIZE]
    signature = transaction_bytes[3 * HASH_SIZE :]

    return Transaction(
        reference_hash=reference_hash,
        sender=sender,
        receiver=receiver,
        signature=signature,
    )


def decode_transactions(
    transaction_counter: int, transactions_bytes: bytes
) -> List[Transaction]:
    """ """
    transactions: List[Transaction] = []

    for i in range(transaction_counter):
        transaction_bytes = transactions_bytes[
            i * TRANSACTION_SIZE : (i + 1) * TRANSACTION_SIZE
        ]
        transaction = decode_transaction(transaction_bytes)

        transactions.append(transaction)

    return transactions


def init_reward(receiver: Hash) -> Transaction:
    """ """
    return Transaction(
        reference_hash=REWARD_HASH,
        sender=REWARD_SENDER,
        receiver=receiver,
        signature=REWARD_SIGNATURE,
    )


def validate_reward(reward: Transaction) -> bool:
    """ """
    is_valid_reference = reward.reference_hash == REWARD_HASH
    is_valid_sender = reward.sender == REWARD_SENDER
    is_valid_signature = reward.signature == REWARD_SIGNATURE

    return is_valid_reference and is_valid_sender and is_valid_signature


@dataclasses.dataclass
class Tree:
    """ """

    tree_hash: Hash
    left: Optional["Tree"]
    right: Optional["Tree"]


def init_merkle_tree(transaction_hashes: List[Hash]) -> Optional[Tree]:
    """ """
    transaction_counter = len(transaction_hashes)

    if transaction_counter == 0:
        return None

    elif transaction_counter == 1:
        return Tree(tree_hash=transaction_hashes[0], left=None, right=None)

    bit_length = transaction_counter.bit_length()
    largest_power_of_two = 1 << (bit_length - 1)

    if largest_power_of_two == transaction_counter:
        divider_index = transaction_counter >> 1
    else:
        divider_index = largest_power_of_two

    left = init_merkle_tree(transaction_hashes[:divider_index])
    right = init_merkle_tree(transaction_hashes[divider_index:])

    assert left is not None and right is not None
    left_hash = left.tree_hash
    right_hash = right.tree_hash

    tree_hash = hashlib.sha256(left_hash + right_hash).digest()

    return Tree(tree_hash=tree_hash, left=left, right=right)


def find_merkle_path(merkle_tree: Tree, transaction_hash: Hash) -> Optional[List[Hash]]:
    """ """
    queue: List[Tuple[List[Hash], Tree]] = [([merkle_tree.tree_hash], merkle_tree)]

    while queue:
        path, current_tree = queue.pop(0)

        if current_tree.tree_hash == transaction_hash:
            if len(path) > 1:
                path += [transaction_hash]

            return path[::-1]

        left = current_tree.left
        right = current_tree.right

        if left is not None:
            assert right is not None
            queue.append((path + [right.tree_hash], left))

        if right is not None:
            assert left is not None
            queue.append((path + [left.tree_hash], right))

    return None


def validate_merkle_path(path: Optional[List[Hash]]):
    """ """
    if path is None:
        return False

    if len(path) == 1:
        return True

    root_hash = path.pop()
    candidate_tree = Tree(tree_hash=path[0], left=None, right=None)

    queue_in = [(candidate_tree.tree_hash, candidate_tree)]
    queue_out = []

    for i, child_hash in enumerate(path[1:]):
        while queue_in:
            current_hash, current_tree = queue_in.pop()

            left_hash = hashlib.sha256(current_hash + child_hash).digest()
            right_hash = hashlib.sha256(child_hash + current_hash).digest()

            left = Tree(tree_hash=left_hash, left=None, right=None)
            right = Tree(tree_hash=right_hash, left=None, right=None)

            current_tree.left = left
            current_tree.right = right

            queue_out += [(left_hash, left)]
            queue_out += [(right_hash, right)]

        queue_in = queue_out.copy()
        queue_out = []

    candidate_hashes = []
    queue = [candidate_tree]

    while queue:
        current_tree = queue.pop(0)

        if current_tree.left is not None:
            queue.append(current_tree.left)

        if current_tree.right is not None:
            queue.append(current_tree.right)

        if current_tree.left is None and current_tree.right is None:
            candidate_hashes.append(current_tree.tree_hash)

    return root_hash in candidate_hashes
