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


def _resolve_path(root: Path, path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = root / path
    return path


def _artifact_dir_for_test(nodeid: str, output_dir: str, root: Path) -> Path:
    safe_nodeid = re.sub(r"[^a-z0-9]+", "-", nodeid.lower()).strip("-")
    return _resolve_path(root, output_dir) / safe_nodeid


def _report_dir(config: pytest.Config) -> Path:
    html_path = getattr(config.option, "htmlpath", None)
    if not html_path:
        return Path(config.rootpath)
    path = _resolve_path(Path(config.rootpath), html_path)
    return path.parent


def _artifact_link(report_dir: Path, file_path: Path) -> str:
    try:
        return str(file_path.relative_to(report_dir))
    except ValueError:
        return file_path.as_posix()


def _image_base64(file_path: Path) -> str:
    # pytest-html self-contained report expects raw base64 for images.
    return b64encode(file_path.read_bytes()).decode("ascii")


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

    artifact_dir = _artifact_dir_for_test(item.nodeid, output_dir, Path(item.config.rootpath))
    report_dir = _report_dir(item.config)

    extras = list(getattr(report, "extras", []))
    screenshot_path = artifact_dir / "test-failed-1.png"
    if screenshot_path.exists():
        extras.append(pytest_html.extras.image(_image_base64(screenshot_path), name="Failure Screenshot"))
        extras.append(
            pytest_html.extras.url(_artifact_link(report_dir, screenshot_path), name="Open Failure Screenshot")
        )

    linked_artifacts = [
        (artifact_dir / "video.webm", "Failure Video"),
        (artifact_dir / "trace.zip", "Playwright Trace"),
    ]
    for file_path, label in linked_artifacts:
        if file_path.exists():
            extras.append(pytest_html.extras.url(_artifact_link(report_dir, file_path), name=label))
    report.extras = extras


@pytest.fixture
def login_page(page: Page, ui_base_url: str) -> LoginPage:
    login_page = LoginPage(page, base_url=ui_base_url)
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

