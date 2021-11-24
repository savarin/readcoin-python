import hashlib

import transactions as transacts


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

    tree_nil = transacts.init_merkle_tree([])
    assert tree_nil is None

    tree_1 = transacts.init_merkle_tree([hash_1])
    assert tree_1.tree_hash == hash_1
    assert tree_1.left is None
    assert tree_1.right is None

    tree_12 = transacts.init_merkle_tree([hash_1, hash_2])
    assert tree_12.tree_hash == hash_12
    assert tree_12.left.tree_hash == hash_1
    assert tree_12.right.tree_hash == hash_2

    tree_123 = transacts.init_merkle_tree([hash_1, hash_2, hash_3])
    assert tree_123.tree_hash == hash_123
    assert tree_123.left.tree_hash == hash_12
    assert tree_123.right.tree_hash == hash_3

    tree_1234 = transacts.init_merkle_tree([hash_1, hash_2, hash_3, hash_4])
    assert tree_1234.tree_hash == hash_1234
    assert tree_1234.left.tree_hash == hash_12
    assert tree_1234.right.tree_hash == hash_34


def test_find_merkle_path():
    """ """
    hash_1 = (1).to_bytes(32, byteorder="big")
    hash_2 = (2).to_bytes(32, byteorder="big")
    hash_3 = (3).to_bytes(32, byteorder="big")
    hash_4 = (4).to_bytes(32, byteorder="big")

    hash_12 = hashlib.sha256(hash_1 + hash_2).digest()
    hash_123 = hashlib.sha256(hash_12 + hash_3).digest()
    hash_34 = hashlib.sha256(hash_3 + hash_4).digest()
    hash_1234 = hashlib.sha256(hash_12 + hash_34).digest()

    tree_1 = transacts.init_merkle_tree([hash_1])
    tree_12 = transacts.init_merkle_tree([hash_1, hash_2])
    tree_123 = transacts.init_merkle_tree([hash_1, hash_2, hash_3])
    tree_1234 = transacts.init_merkle_tree([hash_1, hash_2, hash_3, hash_4])

    path_1 = transacts.find_merkle_path(tree_1, hash_1)
    assert len(path_1) == 1
    assert path_1[0] == hash_1

    path_2 = transacts.find_merkle_path(tree_1, hash_2)
    assert path_2 is None

    path_3 = transacts.find_merkle_path(tree_12, hash_1)
    assert len(path_3) == 3
    assert path_3[0] == hash_1
    assert path_3[1] == hash_2
    assert path_3[2] == hash_12

    path_4 = transacts.find_merkle_path(tree_12, hash_2)
    assert len(path_3) == 3
    assert path_4[0] == hash_2
    assert path_4[1] == hash_1
    assert path_4[2] == hash_12

    path_5 = transacts.find_merkle_path(tree_123, hash_3)
    assert len(path_5) == 3
    assert path_5[0] == hash_3
    assert path_5[1] == hash_12
    assert path_5[2] == hash_123

    path_6 = transacts.find_merkle_path(tree_123, hash_4)
    assert path_6 is None

    path_7 = transacts.find_merkle_path(tree_1234, hash_1)
    assert len(path_7) == 4
    assert path_7[0] == hash_1
    assert path_7[1] == hash_2
    assert path_7[2] == hash_34
    assert path_7[3] == hash_1234

    path_8 = transacts.find_merkle_path(tree_1234, hash_4)
    assert len(path_8) == 4
    assert path_8[0] == hash_4
    assert path_8[1] == hash_3
    assert path_8[2] == hash_12
    assert path_8[3] == hash_1234

    assert transacts.validate_merkle_path(path_1)
    assert not transacts.validate_merkle_path(path_2)
    assert transacts.validate_merkle_path(path_3)
    assert transacts.validate_merkle_path(path_4)
    assert transacts.validate_merkle_path(path_5)
    assert not transacts.validate_merkle_path(path_6)
    assert transacts.validate_merkle_path(path_7)
    assert transacts.validate_merkle_path(path_8)
