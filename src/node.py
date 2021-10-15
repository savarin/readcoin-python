import os
import dataclasses
import socket
import sys

import dotenv

import helpers


dotenv.load_dotenv()

HQ_IP = os.getenv("HQ_IP")
HQ_PORT = 6000

NODE_IP = os.getenv("NODE_IP")
NODE_PORTS = [7000, 8000, 9000]


@dataclasses.dataclass
class Node:
    """ """

    sock: socket.socket


def init_node(port) -> Node:
    """ """
    assert NODE_IP is not None
    sock = helpers.bind_socket(NODE_IP, port)

    return Node(sock=sock)


def listen(node: Node):
    """ """
    while True:
        try:
            node.sock.settimeout(3)
            message, _ = node.sock.recvfrom(1024)
            print(message)
        except socket.timeout:
            print(".")


if __name__ == "__main__":
    port = int(sys.argv[1])
    assert port in NODE_PORTS

    node = init_node(port)
    listen(node)
