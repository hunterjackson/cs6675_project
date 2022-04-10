from abc import ABC, abstractmethod
from typing import Iterable, Final, Tuple, Optional

from chain_utils import sha256_hash_block
from entries import BaseEntry, RootEntry

BLOCK_HASH_LEADING_ZEROS = 3


class BaseBlock(ABC):

    @property
    @abstractmethod
    def previous_block(self) -> 'BaseBlock':
        ...

    @property
    @abstractmethod
    def entries(self) -> Tuple[BaseEntry]:
        ...

    @property
    @abstractmethod
    def sha256_hash(self) -> bytes:
        ...


class Block(BaseBlock):

    def __init__(self, previous_block: 'BaseBlock', entries: Iterable[BaseEntry]):
        self._entries: Final[Tuple[BaseEntry]] = tuple(i for i in entries)
        assert len(self._entries) > 0, 'must be at least one entry in a block'
        self._previous_block: Final[BaseBlock] = previous_block
        self._sha256_hash: Optional[bytes] = None

    @property
    def sha256_hash(self) -> bytes:
        if self._sha256_hash is None:
            self._sha256_hash = sha256_hash_block(self)
        return self._sha256_hash

    @property
    def previous_block(self) -> 'BaseBlock':
        return self._previous_block

    @property
    def entries(self) -> Tuple[BaseEntry]:
        return self._entries


class RootBlock(BaseBlock):
    _SHA_256_HASH: Final[bytes] = (0).to_bytes(length=8, byteorder='big', signed=False)
    _INSTANCE: Optional['RootBlock'] = None

    def __init__(self):
        if RootBlock._INSTANCE is not None:
            raise Exception('This is a singleton class that should never be called, use get_instance')
        RootBlock._INSTANCE = self

    @property
    def previous_block(self) -> 'BaseBlock':
        return self

    @property
    def entries(self) -> Tuple[BaseEntry]:
        return RootEntry.get_instance(),

    @property
    def sha256_hash(self) -> bytes:
        return RootBlock._SHA_256_HASH

    @staticmethod
    def get_instance():
        if RootBlock._INSTANCE is None:
            RootBlock()
        return RootBlock._INSTANCE
