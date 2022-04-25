import os
from hashlib import sha256
from os import listdir
from pathlib import Path
from random import choice
from tempfile import mkstemp

import requests
from fastecdsa.curve import P256
from fastecdsa.ecdsa import verify
from fastecdsa.encoding.der import DEREncoder
from fastecdsa.keys import import_key
from fastecdsa.point import Point

if __name__ == '__main__':
    documents_dir = Path('/home/hunter/bin/cs6675_project/files')

    for _ in range(10):
        documents = listdir(documents_dir)
        d = choice(documents)
        assert isinstance(d, str)
        response = requests.get(f'http://localhost:8000?doc_id={d}')
        assert response.status_code == 200
        key = response.headers['X-Public-Key']
        try:
            _, f = mkstemp(text=True)
            h = bytes.fromhex(key)
            string = h.decode('utf8')
            with open(f, 'w') as _f:
                _f.write(string)
            _, public_key = import_key(f, P256, public=True)
            assert isinstance(public_key, Point)
            r, s = DEREncoder.decode_signature(bytes.fromhex(d))
            assert verify((r, s), sha256(response.text.encode('utf8')).digest(), Q=public_key)
            print(f'validated authenticity and integrity of doc_id={d}')

        finally:
            os.remove(f)
