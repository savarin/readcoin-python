from typing import Tuple, Union
import dataclasses
import hashlib

import cryptography
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


SIGNATURE_ALGORITHM = ec.ECDSA(algorithm=cryptography.hazmat.primitives.hashes.SHA256())
ENCODING = serialization.Encoding.PEM
PUBLIC_FORMAT = serialization.PublicFormat.SubjectPublicKeyInfo
PRIVATE_FORMAT = serialization.PrivateFormat.PKCS8


def sign(private_key: ec.EllipticCurvePrivateKey, message: bytes) -> bytes:
    """ """
    return private_key.sign(message, SIGNATURE_ALGORITHM)


def verify(
    signature: bytes, public_key: ec.EllipticCurvePublicKey, message: bytes
) -> bool:
    """ """
    try:
        public_key.verify(signature, message, SIGNATURE_ALGORITHM)

    except cryptography.exceptions.InvalidSignature:
        return False

    return True


def save_key_pair(
    public_key: ec.EllipticCurvePublicKey,
    private_key: ec.EllipticCurvePrivateKey,
    name_prefix: str = "",
    require_password: bool = True,
):
    """ """
    password = None
    encryption_algorithm: Union[
        serialization.NoEncryption, serialization.BestAvailableEncryption
    ] = serialization.NoEncryption()

    if require_password:
        password = input("password: ").encode()
        encryption_algorithm = serialization.BestAvailableEncryption(password=password)

    serialized_public = public_key.public_bytes(encoding=ENCODING, format=PUBLIC_FORMAT)
    serialized_private = private_key.private_bytes(
        encoding=ENCODING,
        format=PRIVATE_FORMAT,
        encryption_algorithm=encryption_algorithm,
    )

    with open(f"src/{name_prefix}public.pem", "wb") as f:
        f.write(serialized_public)

    with open(f"src/{name_prefix}private.pem", "wb") as f:
        f.write(serialized_private)


def load_key_pair(
    name_prefix: str = "", require_password: bool = True
) -> Tuple[ec.EllipticCurvePublicKey, ec.EllipticCurvePrivateKey]:
    """ """
    password = None

    if require_password:
        password = input("password: ").encode()

    with open(f"src/{name_prefix}public.pem", "rb") as f:
        serialized_public = f.read()

    with open(f"src/{name_prefix}private.pem", "rb") as f:
        serialized_private = f.read()

    public_key = serialization.load_pem_public_key(serialized_public)
    private_key = serialization.load_pem_private_key(
        serialized_private, password=password
    )

    assert isinstance(public_key, ec.EllipticCurvePublicKey)
    assert isinstance(private_key, ec.EllipticCurvePrivateKey)

    return public_key, private_key


@dataclasses.dataclass
class Account:
    """ """

    address: bytes
    port: int
    public_key: ec.EllipticCurvePublicKey
    private_key: ec.EllipticCurvePrivateKey


def init_account(port: int) -> Account:
    """ """
    private_key = ec.generate_private_key(curve=ec.SECP256K1())
    public_key = private_key.public_key()

    address = hashlib.sha256(
        public_key.public_bytes(
            encoding=ENCODING,
            format=PUBLIC_FORMAT,
        )
    ).digest()

    return Account(
        address=address, port=port, public_key=public_key, private_key=private_key
    )
