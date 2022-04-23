#!/usr/bin/env python3
from hashlib import sha256
from timeit import Timer
from typing import Tuple
from random import randint

BYTES_DOCUMENT_ENTRY = 201  # number of bytes in a block with a single document entry


def calculate_nonce(p: bytes, __num_leading_zeros: int) -> int:
    hash_builder = sha256(p)
    for nonce in range(2 ** 64):
        _hash_builder = hash_builder.copy()  # copy to avoid wasting
        _hash_builder.update(nonce.to_bytes(8, 'little', signed=False))
        block_hash = _hash_builder.digest()  # 32 bytes long

        # number of leading bytes that must be zero
        zero_byte_length = __num_leading_zeros // 8
        if any(block_hash[i] != 0 for i in range(zero_byte_length)):
            continue

        # number of bits that must be zero in the leading non-zero byte
        zero_bit_length = __num_leading_zeros % 8
        if (block_hash[zero_byte_length] >> (8 - zero_bit_length)) == 0:
            return nonce
    raise Exception('Unable to find appropriate nonce')


def calculate_hashes(_payloads: Tuple[bytes], _num_leading_zeros: int):
    for p in _payloads:
        calculate_nonce(p, _num_leading_zeros)


if __name__ == '__main__':

    random_integers = tuple(randint(0, 2 ** BYTES_DOCUMENT_ENTRY) for _ in range(25))
    payloads = tuple(i.to_bytes(BYTES_DOCUMENT_ENTRY, 'little', signed=False) for i in random_integers)
    # print(len(payloads))
    print('num_leading_zeros, seconds_per_hash')
    for num_leading_zeros in range(0, 33):
        timer = Timer(lambda: calculate_hashes(payloads, num_leading_zeros))
        passes, seconds = timer.autorange()  # guarantees the test will take at least 0.2 seconds to run
        print(f'{num_leading_zeros}, {seconds / (passes * len(payloads))}')
        # print(f'{num_leading_zeros}, {seconds}')
