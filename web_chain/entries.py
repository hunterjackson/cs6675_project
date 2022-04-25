from abc import ABC, abstractmethod
from typing import Final, Optional

import chain_utils
from chain_utils import bytes_32_validator, bytes_64_validator


class BaseEntry(ABC):

    @property
    @abstractmethod
    def sha256_hash(self) -> bytes:
        ...

    @property
    @abstractmethod
    def previous_entry(self) -> 'BaseEntry':
        ...


class RootEntry(BaseEntry):
    _INSTANCE: Optional['RootEntry'] = None
    _SHA_256_HASH: Final[bytes] = (0).to_bytes(length=8, byteorder='big')

    """
    Special entry that is only used for the root of the chain
    """

    def __init__(self):
        if RootEntry._INSTANCE is not None:
            raise Exception('This is a singleton class that should never be called, use get_instance')
        RootEntry._INSTANCE = self

    @staticmethod
    def get_instance() -> 'RootEntry':
        if RootEntry._INSTANCE is None:
            RootEntry()
        return RootEntry._INSTANCE

    @property
    def previous_entry(self) -> 'RootEntry':
        return self

    @property
    def sha256_hash(self) -> bytes:
        return RootEntry._SHA_256_HASH


class BaseDocumentEntry(BaseEntry, ABC):

    @property
    @abstractmethod
    def doc_id(self) -> bytes:
        ...

    @property
    @abstractmethod
    def public_key(self) -> bytes:
        ...


class DocumentPublishEntry(BaseDocumentEntry):

    def __init__(self, previous_entry: BaseEntry, doc_id: bytes, public_key: bytes):
        self._previous_entry: Final[BaseEntry] = previous_entry
        self._doc_id: Final[bytes] = doc_id
        self._public_key: Final[bytes] = public_key
        self._sha256_hash: Optional[bytes] = None

    @property
    def sha256_hash(self) -> bytes:
        if self._sha256_hash is None:
            self._sha256_hash = chain_utils.sha256_hash_entry(self)
        return self._sha256_hash

    @property
    def previous_entry(self) -> 'BaseEntry':
        return self._previous_entry

    @property
    def doc_id(self) -> bytes:
        return self._doc_id

    @property
    def public_key(self) -> bytes:
        return self._public_key


class DocumentUpdateEntry(BaseDocumentEntry):
    PREV_DOC_ID_KEY: Final[bytes] = 'previous_doc_id'.encode('utf8')

    def __init__(self, previous_entry: BaseEntry, previous_doc_id: bytes, doc_id: bytes, public_key: bytes):
        self._previous_entry: Final[BaseEntry] = previous_entry
        self.previous_doc_id: Final[bytes] = bytes_32_validator(previous_doc_id)
        self._doc_id: Final[bytes] = bytes_32_validator(doc_id)
        self._public_key: Final[bytes] = bytes_32_validator(public_key)
        self._sha256_hash: Optional[bytes] = None

    @property
    def sha256_hash(self) -> bytes:
        if self._sha256_hash is None:
            self._sha256_hash = chain_utils.sha256_hash_entry(self)
        return self._sha256_hash

    @property
    def previous_entry(self) -> 'BaseEntry':
        return self._previous_entry

    @property
    def doc_id(self) -> bytes:
        return self._doc_id

    @property
    def public_key(self) -> bytes:
        return self._public_key


class HostLocationEntry(BaseEntry):

    def __init__(self, previous_entry: BaseEntry, ipaddress: bytes, public_key: bytes):
        self._previous_entry: Final[BaseEntry] = previous_entry
        self._sha256_entry: Optional[bytes] = None
        self.ipaddress: Final[bytes] = ipaddress
        self.public_key: Final[bytes] = bytes_64_validator(public_key)

    @property
    def sha256_hash(self) -> bytes:
        if self._sha256_entry is None:
            self._sha256_entry = chain_utils.sha256_hash_entry(self)
        return self._sha256_entry

    @property
    def previous_entry(self) -> 'BaseEntry':
        return self._previous_entry
