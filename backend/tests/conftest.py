import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Tests must run with no provider keys configured (mock fallback everywhere).
os.environ["QVERIS_API_KEY"] = ""
os.environ["DEEPSEEK_API_KEY"] = ""
os.environ["DATABASE_URL"] = "sqlite:///./test_alphaquantpro.db"

import pytest  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _cleanup_db():
    yield
    for name in ("test_alphaquantpro.db",):
        try:
            os.remove(name)
        except FileNotFoundError:
            pass
