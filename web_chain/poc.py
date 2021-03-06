import os
from pathlib import Path
from threading import Thread, Lock
from typing import Optional, Literal, Final
from uuid import uuid4

from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from fastecdsa import keys, curve
from fastecdsa.curve import P256
from fastecdsa.keys import export_key

from blocks import RootBlock, BaseBlock, Block
from chain_utils import doc_id
from entries import HostLocationEntry, DocumentPublishEntry, BaseDocumentEntry, BaseEntry

INDIANESS: Final[Literal["little"]] = 'little'

DOC_TEMPLATE: Final[str] = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Example Document</title>
    <p>This is an example document</p>
    <p>{}</p>
</head>
<body>

</body>
</html>'''


class ChainState:

    def __init__(self):
        self._lock: Final[Lock] = Lock()
        self._tail: BaseBlock = RootBlock.get_instance()

    @property
    def lock(self):
        return self._lock

    @property
    def tail(self) -> BaseBlock:
        return self._tail

    @tail.setter
    def tail(self, block: BaseBlock):
        assert block.previous_block is self.tail
        self._tail = block


class WebChainThread(Thread):

    def __init__(self, chain_state: ChainState, storage_dir: Path, num_blocks_to_gen: Optional[int] = None) -> None:
        super().__init__()
        self.chain_state: Final[ChainState] = chain_state
        self.storage_dir: Final[Path] = storage_dir
        self.private_key, self.public_key = keys.gen_keypair(curve.P256)
        self.public_key_bytes: Final[bytes] = self.private_key.to_bytes(64, INDIANESS)
        self.ip_address: Final[bytes] = bytes([127, 0, 0, 1])
        self.num_blocks_to_gen: Optional[int] = num_blocks_to_gen
        self.hault = False

    def stop(self):
        self.hault = True

    def run(self) -> None:
        super().run()

        with self.chain_state.lock:
            host_location = HostLocationEntry(self.chain_state.tail.entries[-1], self.ip_address,
                                              self.public_key_bytes)
            block = Block(self.chain_state.tail, [host_location])
            assert block.nonce is not None
            self.chain_state.tail = block

        while not self.hault and (self.num_blocks_to_gen is None or self.num_blocks_to_gen > 0):

            with self.chain_state.lock:
                doc_contents = DOC_TEMPLATE.format(str(uuid4()))
                _doc_id = doc_id(doc_contents, self.private_key)
                entry = DocumentPublishEntry(self.chain_state.tail.entries[-1], _doc_id,
                                             export_key(self.public_key, P256).encode('utf8'))
                block = Block(self.chain_state.tail, [entry])
                assert block.nonce is not None
                self.chain_state.tail = block
                with open(self.storage_dir / _doc_id.hex(), 'w+') as f:
                    f.write(doc_contents)

            if self.num_blocks_to_gen is not None:
                self.num_blocks_to_gen -= 1


def cleanup_files(_dir: Path):
    for f in os.listdir(_dir):
        os.remove(_dir / f)


document_dir = Path('/home/hunter/bin/cs6675_project/files')
state = ChainState()
threads = [WebChainThread(state, document_dir), WebChainThread(state, document_dir),
           WebChainThread(state, document_dir)]
app = FastAPI(on_startup=[lambda: [t.start() for t in threads]],
              on_shutdown=[lambda: [t.stop() for t in threads], lambda: [t.join() for t in threads],
                           lambda: cleanup_files(document_dir)])


@app.get('/', response_class=HTMLResponse)
def get_document(doc_id: str, response: Response):
    try:
        with open(document_dir / doc_id) as f:
            contents = f.read()
        response.headers['Cache-Control'] = 'public, max-age=31557600, immutable'
        response.headers['ETag'] = doc_id
        tail_entry: BaseEntry = state.tail.entries[-1]
        doc_id_bytes = bytes.fromhex(doc_id)
        while True:
            if tail_entry is tail_entry.previous_entry:
                raise Exception("Cannot find entry")
            if isinstance(tail_entry, BaseDocumentEntry) and tail_entry.doc_id == doc_id_bytes:
                break
            tail_entry = tail_entry.previous_entry
        response.headers['X-Public-Key'] = tail_entry.public_key.hex()
        return contents
    except FileNotFoundError:
        response.status_code = 404
        return f'''<!DOCTYPE html>
        <html lang=en>
        <title>404 Unable to locate document</title>
        <p>The requested document id <code>{doc_id}</code> was not found in WebChain</p>
        '''
