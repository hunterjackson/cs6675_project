from pathlib import Path

from web_chain.blocks import RootBlock
from web_chain.poc import WebChainThread, ChainState


def test_chain_thread(tmpdir):
    state = ChainState()
    thread = WebChainThread(chain_state=state, storage_dir=Path(tmpdir), num_blocks_to_gen=1)
    thread.start()
    thread.join()

    assert state.tail is not RootBlock.get_instance()
