from hashlib import sha256
from typing import Final, Optional

PREV_ENTRY_HASH_KEY: Final[bytes] = 'previous_entry_hash'.encode('utf8')
DOC_ID_KEY: Final[bytes] = 'doc_id'.encode('utf8')
PEK_KEY: Final[bytes] = 'public_key'.encode('utf8')
PREV_DOC_ID_KEY: Final[bytes] = 'previous_doc_id'.encode('utf8')
IP_ADDRESS_KEY: Final[bytes] = 'ip_address'.encode('utf8')
BLOCK_SEPERATOR: Final[bytes] = ':'.encode('utf8')

MIN_INT = -2 ** 63
MAX_INT = 2 ** 63 - 1

BLOCK_HASH_LEADING_ZEROS = 3


def bytes_256_validator(payload: bytes) -> bytes:
    # TODO: 256 bits is 32 bytes....wtf duh
    assert isinstance(payload, bytes)
    assert len(payload) == 32
    return payload


def int_64_bit_validator(value: int):
    assert MIN_INT <= value <= MAX_INT
    return value


def sha256_hash_entry(entry: 'chain.BaseEntry') -> bytes:
    from web_chain.entries import BaseDocumentEntry, DocumentUpdateEntry, RootEntry, HostLocationEntry

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
    return (hash_value[0] >> 5) == 0


def sha256_hash_block(block: 'web_chain.blocks.BaseBlock', nonce: Optional[int]):
    # TODO: mining
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
