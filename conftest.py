import os

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    # ── UI options ────────────────────────────────────────────────────────────
    ui_group = parser.getgroup("ui")
    ui_group.addoption(
        "--ui-base-url",
        action="store",
        default=None,
        help=(
            "Override base URL for UI tests. "
            "Falls back to $UI_BASE_URL env var, then 'ui_base_url' in pytest.ini."
        ),
    )

    parser.addini(
        "ui_base_url",
        "Base URL for UI tests (e.g. https://www.saucedemo.com)",
        default="https://www.saucedemo.com",
    )

    # ── API options ───────────────────────────────────────────────────────────
    api_group = parser.getgroup("api")
    api_group.addoption(
        "--api-base-url",
        action="store",
        default=None,
        help=(
            "Override base URL for API tests. "
            "Falls back to $API_BASE_URL env var, then 'api_base_url' in pytest.ini."
        ),
    )
    api_group.addoption(
        "--api-timeout",
        action="store",
        default=None,
        help="Override request timeout (seconds) for API tests",
    )

    parser.addini(
        "api_base_url",
        "Base URL for API tests",
        default="https://jsonplaceholder.typicode.com",
    )
    parser.addini(
        "api_timeout",
        "Request timeout (seconds) for API tests",
        default="10",
    )


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def ui_base_url(pytestconfig: pytest.Config) -> str:
    """Resolve the UI base URL using the priority chain:

    1. ``--ui-base-url`` CLI flag
    2. ``UI_BASE_URL`` environment variable
    3. ``ui_base_url`` value in ``pytest.ini``

    Trailing slashes are stripped so callers can always do ``base_url + "/path"``.
    """
    url = (
        pytestconfig.getoption("ui_base_url")
        or os.environ.get("UI_BASE_URL")
        or pytestconfig.getini("ui_base_url")
    )
    return url.rstrip("/")

