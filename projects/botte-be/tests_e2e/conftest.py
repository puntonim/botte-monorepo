from pathlib import Path

import pytest

CURR_DIR = Path(__file__).parent
ROOT_DIR = CURR_DIR.parent


@pytest.fixture(scope="session")
def monkeysession(request):
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()
