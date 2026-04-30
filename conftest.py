import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    api_group = parser.getgroup("api")
    api_group.addoption(
        "--api-base-url",
        action="store",
        default=None,
        help="Override base URL for API tests",
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
