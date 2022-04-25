from hashlib import sha256
from typing import Final, Optional

from fastecdsa import ecdsa
from fastecdsa.encoding.der import DEREncoder

PREV_ENTRY_HASH_KEY: Final[bytes] = 'previous_entry_hash'.encode('utf8')
DOC_ID_KEY: Final[bytes] = 'doc_id'.encode('utf8')
PEK_KEY: Final[bytes] = 'public_key'.encode('utf8')
PREV_DOC_ID_KEY: Final[bytes] = 'previous_doc_id'.encode('utf8')
IP_ADDRESS_KEY: Final[bytes] = 'ip_address'.encode('utf8')
BLOCK_SEPERATOR: Final[bytes] = ':'.encode('utf8')

MIN_INT = -2 ** 63
MAX_INT = 2 ** 63 - 1

BLOCK_HASH_LEADING_ZEROS = 18


def bytes_32_validator(payload: bytes) -> bytes:
    assert isinstance(payload, bytes)
    assert len(payload) == 32
    return payload


def bytes_64_validator(payload: bytes) -> bytes:
    assert isinstance(payload, bytes)
    assert len(payload) == 64
    return payload


def int_64_bit_validator(value: int):
    assert MIN_INT <= value <= MAX_INT
    return value


def doc_id(doc_contents: str, private_key) -> bytes:
    doc_hash = sha256(doc_contents.encode('utf8')).digest()
    a, b = ecdsa.sign(doc_hash, private_key)
    return DEREncoder.encode_signature(a, b)


def sha256_hash_entry(entry: 'chain.BaseEntry') -> bytes:
    from entries import BaseDocumentEntry, DocumentUpdateEntry, RootEntry, HostLocationEntry

    if isinstance(entry, RootEntry):
        return entry.sha256_hash  # fixed hash value for root

    hash_builder = sha256()
    hash_builder.update(PREV_ENTRY_HASH_KEY)
    hash_builder.update(entry.previous_entry.sha256_hash)

    if isinstance(entry, BaseDocumentEntry):
        if isinstance(entry, DocumentUpdateEntry):
            hash_builder.update(PREV_DOC_ID_KEY)
            hash_builder.update(entry.previous_doc_id)

        hash_builder.update(DOC_ID_KEY)
        hash_builder.update(entry.doc_id)
        hash_builder.update(PEK_KEY)
        hash_builder.update(entry.public_key)
    elif isinstance(entry, HostLocationEntry):
        hash_builder.update(IP_ADDRESS_KEY)
        hash_builder.update(entry.ipaddress)
        hash_builder.update(PEK_KEY)
        hash_builder.update(entry.public_key)

    return hash_builder.digest()


def validate_block_hash(hash_value: bytes):
    assert len(hash_value) == 32
    # number of leading bytes that must be zero
    zero_byte_length = BLOCK_HASH_LEADING_ZEROS // 8
    if any(hash_value[i] != 0 for i in range(zero_byte_length)):
        return False

    # number of bits that must be zero in the leading non-zero byte
    zero_bit_length = BLOCK_HASH_LEADING_ZEROS % 8
    if (hash_value[zero_byte_length] >> (8 - zero_bit_length)) == 0:
        return True
    return False


def sha256_hash_block(block: 'web_chain.blocks.BaseBlock', nonce: Optional[int]):
    hash_builder = _init_hash_builder(block)
    if nonce is not None:
        hash_builder.update(nonce)
        hash_value = hash_builder.digest()
        assert validate_block_hash(hash_value)
        return nonce, hash_value

    for nonce in range(MIN_INT, MAX_INT):
        _hash_builder = hash_builder.copy()
        _hash_builder.update(nonce.to_bytes(length=8, byteorder='big', signed=True))
        hash_value = _hash_builder.digest()
        if validate_block_hash(hash_value):
            return nonce, hash_value
    raise ValueError(f'Unable to find hash value with {BLOCK_HASH_LEADING_ZEROS} leading zeros')


def _init_hash_builder(block: 'web_chain.blocks.BaseBlock'):
    hash_builder = sha256()
    hash_builder.update(block.previous_block.sha256_hash)
    for entry in block.entries:
        hash_builder.update(BLOCK_SEPERATOR)
        hash_builder.update(entry.sha256_hash)
    return hash_builder
