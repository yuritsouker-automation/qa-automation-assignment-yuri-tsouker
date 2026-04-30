import json
import os

import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "test_data", "credentials.json")

with open(CREDENTIALS_PATH) as f:
    _credentials = json.load(f)


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    login_page = LoginPage(page)
    login_page.navigate()
    return login_page


@pytest.fixture
def login_as_user(login_page: LoginPage):
    def _login(user_key: str) -> None:
        creds = _credentials[user_key]
        login_page.login(username=creds["username"], password=creds["password"])

    return _login


@pytest.fixture
def logout_after_test(page: Page):
    yield
    login_page = LoginPage(page)
    if login_page.burger_button.is_visible():
        login_page.logout()

