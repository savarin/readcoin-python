import dataclasses
import dotenv
import os
import random
import socket
import sys
import time


dotenv.load_dotenv()

NODE_IP = os.getenv("NODE_IP")
NODE_PORTS = [7000, 8000, 9000]


def bind_socket(ip_address: str, port: int) -> socket.socket:
    """ """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip_address, port))
    return sock


@dataclasses.dataclass
class Node:
    """ """

    port: int
    sock: socket.socket
    blockchain: bytes
    block_counter: int


def init_node(port: int, blockchain: bytes = b"", block_counter: int = 0) -> Node:
    """ """
    assert NODE_IP is not None
    sock = bind_socket(NODE_IP, port)

    return Node(
        port=port, sock=sock, blockchain=blockchain, block_counter=block_counter
    )


def broadcast(node: Node, message: bytes):
    """ """
    for node_port in NODE_PORTS:
        if node_port == node.port:
            continue

        node.sock.sendto(message, (NODE_IP, node_port))


def run(node: Node):
    """ """
    while True:
        try:
            node.sock.settimeout(1)
            message, _ = node.sock.recvfrom(9216)

            node_port = int.from_bytes(message[:2], byteorder="big")
            sleep_time = message[2]

            print(f"OTHER {node_port} sleep for {sleep_time} seconds...")

        except socket.timeout:
            sleep_time = random.randint(1, 9)
            message = node.port.to_bytes(2, byteorder="big") + sleep_time.to_bytes(
                1, byteorder="big"
            )

            broadcast(node, message)
            print(f"SELF {node.port} sleep for {sleep_time} seconds...")

            time.sleep(sleep_time)


if __name__ == "__main__":
    port = int(sys.argv[1])
    assert port in NODE_PORTS

    node = init_node(port)
    run(node)
