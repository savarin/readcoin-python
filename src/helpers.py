import socket


def bind_socket(ip_address: str, port: int) -> socket.socket:
    """ """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip_address, port))
    return sock
