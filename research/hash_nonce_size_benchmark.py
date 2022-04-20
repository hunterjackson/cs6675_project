#!/usr/bin/env python3
from hashlib import sha256
from timeit import Timer
from typing import List

BYTES_DOCUMENT_ENTRY = 127  # number of bytes in a document entry


def calculate_hashes(payloads: List[bytes], num_leading_zeros: int):
    for p in payloads:
        hash_builder = sha256(p)
        for nonce in range(2 ** 64):
            _hash_builder = hash_builder.copy()  # copy to avoid wasting
            _hash_builder.update(nonce.to_bytes(8, 'big', signed=False))
            block_hash = _hash_builder.digest()
            assert len(block_hash) == 32

            # number of leading bytes that must be zero
            zero_byte_length = num_leading_zeros // 8
            if any(block_hash[i] != 0 for i in range(zero_byte_length)):
                continue

            # number of bits that must be zero in the leading non-zero byte
            zero_bit_length = num_leading_zeros % 8
            if (block_hash[zero_byte_length + 1] >> (8 - zero_bit_length)) == 0:
                break


if __name__ == '__main__':
    payloads = [i.to_bytes(BYTES_DOCUMENT_ENTRY, 'big', signed=False) for i in range(100, 200)]
    payloads += [i.to_bytes(BYTES_DOCUMENT_ENTRY * 3, 'big', signed=False) for i in range(200, 300)]
    payloads += [i.to_bytes(BYTES_DOCUMENT_ENTRY * 5, 'big', signed=False) for i in range(300, 400)]
    print('num_leading_zeros, seconds_per_hash')
    for num_leading_zeros in range(1, 33):
        timer = Timer(lambda: calculate_hashes(payloads, num_leading_zeros))
        passes, seconds = timer.autorange()  # guarantees the test will take at least 0.2 seconds to run
        print(f'{num_leading_zeros}, {seconds / (passes * len(payloads))}')
        # print(f'{num_leading_zeros}, {seconds}')
