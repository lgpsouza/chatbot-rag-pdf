import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


@pytest.fixture(autouse=True)
def openai_api_key_fake(monkeypatch):
    """Garante OPENAI_API_KEY isolada em todos os testes sem chamadas reais à API."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-fake-test-key")
