import os

import pytest
import requests

from src.api.client import ApiClient
from src.api.config import ApiConfig


@pytest.fixture(scope="session")
def api_base_url(pytestconfig: pytest.Config) -> str:
    """Resolve the API base URL using the priority chain:

    1. ``--api-base-url`` CLI flag
    2. ``API_BASE_URL`` environment variable
    3. ``api_base_url`` value in ``pytest.ini``
    """
    url = (
        pytestconfig.getoption("api_base_url")
        or os.environ.get("API_BASE_URL")
        or pytestconfig.getini("api_base_url")
    )
    return url.rstrip("/")


@pytest.fixture(scope="session")
def api_timeout(pytestconfig: pytest.Config) -> float:
    configured_timeout = pytestconfig.getoption("api_timeout") or pytestconfig.getini("api_timeout")
    try:
        return float(configured_timeout)
    except ValueError as exc:
        raise pytest.UsageError(
            f"Invalid api_timeout value '{configured_timeout}'. Expected a number."
        ) from exc


@pytest.fixture(scope="session")
def api_config(api_base_url: str, api_timeout: float) -> ApiConfig:
    return ApiConfig(base_url=api_base_url, timeout=api_timeout)


@pytest.fixture(scope="session")
def api_session() -> requests.Session:
    with requests.Session() as session:
        yield session


@pytest.fixture(scope="session")
def api_client(api_session: requests.Session, api_config: ApiConfig) -> ApiClient:
    return ApiClient(session=api_session, config=api_config)

