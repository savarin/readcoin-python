from typing import List
import binascii
import dataclasses
import os
import socket
import sys
import time

import dotenv

import blocks
import helpers


dotenv.load_dotenv()

HQ_IP = os.getenv("HQ_IP")
HQ_PORT = 6000

NODE_IP = os.getenv("NODE_IP")
NODE_PORTS = [7000, 8000, 9000]


@dataclasses.dataclass
class Node:
    """ """

    port: int
    sock: socket.socket


def init_node(port: int) -> Node:
    """ """
    assert NODE_IP is not None
    sock = helpers.bind_socket(NODE_IP, port)

    return Node(port=port, sock=sock)


def listen(node: Node):
    """ """
    blockchain: List[bytes] = []

    prev_hash = (0).to_bytes(32, byteorder="big")
    timestamp = int(time.time())
    nonce = 0

    while True:
        try:
            node.sock.settimeout(1)
            message, _ = node.sock.recvfrom(1024)
            print(message)

        except socket.timeout:
            print(f"nonce: {nonce}")

            is_new_block, block_header, current_hash = blocks.solve_block_header(
                prev_hash, timestamp, nonce, 1000
            )

            if not is_new_block:
                nonce += 1000
                continue

            assert block_header is not None and current_hash is not None
            transaction_counter, transactions = blocks.init_transactions(node.port)
            block = blocks.init_block(block_header, transaction_counter, transactions)

            print(f"block {len(blockchain)}: {binascii.hexlify(current_hash).decode()}")
            blockchain.append(block)

            prev_hash = current_hash
            timestamp = int(time.time())
            nonce = 0


if __name__ == "__main__":
    port = int(sys.argv[1])
    assert port in NODE_PORTS

    node = init_node(port)
    listen(node)
