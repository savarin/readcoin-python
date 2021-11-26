import cryptography
from cryptography.hazmat.primitives.asymmetric import ec


SIGNATURE_ALGORITHM = ec.ECDSA(algorithm=cryptography.hazmat.primitives.hashes.SHA256())


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
