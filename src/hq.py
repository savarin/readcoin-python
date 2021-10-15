import os
import dataclasses
import socket

import dotenv

import helpers


dotenv.load_dotenv()

HQ_IP = os.getenv("HQ_IP")
HQ_PORT = 6000

NODE_IP = os.getenv("NODE_IP")
NODE_PORTS = [7000, 8000, 9000]


@dataclasses.dataclass
class HQ:
    """ """

    sock: socket.socket


def init_hq() -> HQ:
    """ """
    assert HQ_IP is not None
    sock = helpers.bind_socket(HQ_IP, HQ_PORT)

    return HQ(sock=sock)


def listen(hq: HQ):
    """ """
    while True:
        message = bytes.fromhex(input("> "))
        print(message)

        assert NODE_IP is not None
        for node_port in NODE_PORTS:
            hq.sock.sendto(message, (NODE_IP, node_port))


if __name__ == "__main__":
    hq = init_hq()
    listen(hq)
