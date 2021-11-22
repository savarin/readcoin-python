import hashlib

import tree


def test_init_merkle_tree():
    """ """
    hash_1 = (1).to_bytes(32, byteorder="big")
    hash_2 = (2).to_bytes(32, byteorder="big")
    hash_3 = (3).to_bytes(32, byteorder="big")
    hash_4 = (4).to_bytes(32, byteorder="big")

    hash_12 = hashlib.sha256(hash_1 + hash_2).digest()
    hash_123 = hashlib.sha256(hash_12 + hash_3).digest()
    hash_34 = hashlib.sha256(hash_3 + hash_4).digest()
    hash_1234 = hashlib.sha256(hash_12 + hash_34).digest()

    tree_nil = tree.init_merkle_tree([])
    assert tree_nil is None

    tree_1 = tree.init_merkle_tree([hash_1])
    assert tree_1.tree_hash == hash_1
    assert tree_1.left is None
    assert tree_1.right is None

    tree_2 = tree.init_merkle_tree([hash_1, hash_2])
    assert tree_2.tree_hash == hash_12
    assert tree_2.left.tree_hash == hash_1
    assert tree_2.right.tree_hash == hash_2

    tree_3 = tree.init_merkle_tree([hash_1, hash_2, hash_3])
    assert tree_3.tree_hash == hash_123
    assert tree_3.left.tree_hash == hash_12
    assert tree_3.right.tree_hash == hash_3

    tree_4 = tree.init_merkle_tree([hash_1, hash_2, hash_3, hash_4])
    assert tree_4.tree_hash == hash_1234
    assert tree_4.left.tree_hash == hash_12
    assert tree_4.right.tree_hash == hash_34

    path_3 = tree.find_merkle_path(tree_4, hash_3)
    assert path_3[0] == hash_1234
    assert path_3[1] == hash_34
    assert path_3[2] == hash_3
