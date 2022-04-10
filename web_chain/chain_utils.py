from hashlib import sha256
from typing import Final

PREV_ENTRY_HASH_KEY: Final[bytes] = 'previous_entry_hash'.encode('utf8')
DOC_ID_KEY: Final[bytes] = 'doc_id'.encode('utf8')
PEK_KEY: Final[bytes] = 'public_key'.encode('utf8')
PREV_DOC_ID_KEY: Final[bytes] = 'previous_doc_id'.encode('utf8')
IP_ADDRESS_KEY: Final[bytes] = 'ip_address'.encode('utf8')
BLOCK_SEPERATOR: Final[bytes] = ':'.encode('utf8')


def bytes_256_validator(public_key: bytes) -> bytes:
    assert public_key is not None
    assert isinstance(public_key, bytes)
    assert len(public_key) == 8
    return public_key


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


def sha256_hash_block(block: 'web_chain.blocks.BaseBlock'):
    # TODO: mining
    hash_builder = sha256()
    hash_builder.update(block.previous_block.sha256_hash)
    for entry in block.entries:
        hash_builder.update(BLOCK_SEPERATOR)
        hash_builder.update(entry.sha256_hash)
    return hash_builder.digest()
