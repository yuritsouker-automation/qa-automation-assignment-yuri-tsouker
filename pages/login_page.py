import os

from playwright.sync_api import Page


class LoginPage:
    URL_PATH = "/"
    DEFAULT_BASE_URL = "https://www.saucedemo.com"

    def __init__(self, page: Page, base_url: str | None = None):
        self.page = page
        self._base_url = (
            base_url
            or os.environ.get("UI_BASE_URL")
            or self.DEFAULT_BASE_URL
        ).rstrip("/")

        self.username_input = page.locator('[data-test="username"]')
        self.password_input = page.locator('[data-test="password"]')
        self.login_button = page.locator('[data-test="login-button"]')
        self.header_container = page.locator('[data-test="header-container"]')
        self.error_message = page.locator('[data-test="error"]')
        self.error_button = page.locator('[data-test="error-button"]')
        # Burger menu & logout
        self.burger_button = page.locator('.bm-burger-button')
        self.logout_link = page.locator('[data-test="logout-sidebar-link"]')
        # Login page logo (visible after logout)
        self.login_logo = page.locator('.login_logo')

    def navigate(self):
        self.page.goto(f"{self._base_url}{self.URL_PATH}")

    # ...existing code...

    def login(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def wait_for_header(self):
        self.header_container.wait_for(state="visible")

    def logout(self):
        """Open the burger menu, click logout, and wait for the login logo to appear."""
        self.burger_button.click()
        self.logout_link.wait_for(state="visible")
        self.logout_link.click()
        self.login_logo.wait_for(state="visible")
