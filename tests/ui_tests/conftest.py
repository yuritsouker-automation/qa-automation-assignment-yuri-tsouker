import json
import os
import re
from base64 import b64encode
from pathlib import Path

import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "test_data", "credentials.json")

with open(CREDENTIALS_PATH) as f:
    _credentials = json.load(f)


def _artifact_dir_for_test(nodeid: str, output_dir: str) -> Path:
    safe_nodeid = re.sub(r"[^a-z0-9]+", "-", nodeid.lower()).strip("-")
    return Path(output_dir) / safe_nodeid


def _report_dir(config: pytest.Config) -> Path:
    html_path = getattr(config.option, "htmlpath", None)
    if not html_path:
        return Path(config.rootpath)
    path = Path(html_path)
    if not path.is_absolute():
        path = Path(config.rootpath) / path
    return path.parent


def _artifact_link(report_dir: Path, file_path: Path) -> str:
    try:
        return str(file_path.relative_to(report_dir))
    except ValueError:
        return file_path.as_posix()


def _image_data_url(file_path: Path) -> str:
    encoded = b64encode(file_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


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

    pytest_html = item.config.pluginmanager.getplugin("html")
    output_dir = item.config.getoption("output")
    if pytest_html is None or not output_dir:
        return

    artifact_dir = _artifact_dir_for_test(item.nodeid, output_dir)
    report_dir = _report_dir(item.config)

    extras = list(getattr(report, "extras", []))
    screenshot_path = artifact_dir / "test-failed-1.png"
    if screenshot_path.exists():
        extras.append(pytest_html.extras.image(_image_data_url(screenshot_path), name="Failure Screenshot"))

    linked_artifacts = [
        (artifact_dir / "video.webm", "Failure Video"),
        (artifact_dir / "trace.zip", "Playwright Trace"),
    ]
    for file_path, label in linked_artifacts:
        if file_path.exists():
            extras.append(pytest_html.extras.url(_artifact_link(report_dir, file_path), name=label))
    report.extras = extras


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

