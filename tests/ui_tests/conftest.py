import json
import os
import re

import allure
import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "test_data", "credentials.json")

with open(CREDENTIALS_PATH) as f:
    _credentials = json.load(f)


def _artifact_dir_for_test(nodeid: str, output_dir: str) -> str:
    safe_nodeid = re.sub(r"[^a-z0-9]+", "-", nodeid.lower()).strip("-")
    return os.path.join(output_dir, safe_nodeid)


def _attach_if_exists(file_path: str, name: str, attachment_type) -> None:
    if os.path.exists(file_path):
        allure.attach.file(file_path, name=name, attachment_type=attachment_type)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

    if report.when != "teardown":
        return

    failed = getattr(item, "rep_setup", None) and item.rep_setup.failed
    failed = failed or (getattr(item, "rep_call", None) and item.rep_call.failed)
    if not failed:
        return

    output_dir = item.config.getoption("output")
    artifact_dir = _artifact_dir_for_test(item.nodeid, output_dir)

    _attach_if_exists(
        os.path.join(artifact_dir, "test-failed-1.png"),
        name="failure-screenshot",
        attachment_type=allure.attachment_type.PNG,
    )
    _attach_if_exists(
        os.path.join(artifact_dir, "trace.zip"),
        name="playwright-trace",
        attachment_type=allure.attachment_type.ZIP,
    )
    _attach_if_exists(
        os.path.join(artifact_dir, "video.webm"),
        name="failure-video",
        attachment_type="video/webm",
    )



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

