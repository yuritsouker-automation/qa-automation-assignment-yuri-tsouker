import json
import os

import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "test_data", "credentials.json")

EXPECTED_INVALID_CREDENTIALS_ERROR = (
    "Epic sadface: Username and password do not match any user in this service"
)

with open(CREDENTIALS_PATH) as f:
    _credentials = json.load(f)


class TestLogin:
    @pytest.mark.parametrize("user", ["standard_user"], ids=["standard_user"])
    def test_login_standard_user(self, page: Page, user: str):
        """
        Verify that a valid user can log in and then log out successfully.
        Steps:
          1. Navigate to https://www.saucedemo.com/
          2. Enter valid credentials loaded from test_data/credentials.json
          3. Click the login button
          4. Wait for the header container to become visible
          5. Open the burger menu (class="bm-burger-button") and click logout
          6. Wait for the login logo to become visible
        Expected: data-test="header-container" is visible after login;
                  class="login_logo" with text "Swag Labs" is visible after logout.
        """
        login_page = LoginPage(page)

        # 1. Navigate to the app
        login_page.navigate()

        # 2. Login with credentials loaded from test_data/credentials.json
        creds = _credentials[user]
        login_page.login(username=creds["username"], password=creds["password"])

        # 3. Wait until the header container is visible
        login_page.wait_for_header()

        # 4. Assert the header container is indeed visible
        assert login_page.header_container.is_visible(), (
            "header-container should be visible after successful login"
        )

        # 5. Logout via burger menu → data-test="logout-sidebar-link"
        login_page.logout()

        # 6. Assert the login logo "Swag Labs" is visible — confirms we are back on the login page
        assert login_page.login_logo.is_visible(), (
            "class='login_logo' (Swag Labs) should be visible after logout"
        )
        assert login_page.login_logo.inner_text().strip() == "Swag Labs", (
            f"Expected login logo text 'Swag Labs', got {login_page.login_logo.inner_text().strip()!r}"
        )

    @pytest.mark.parametrize("user", ["invalid_user"], ids=["invalid_user"])
    def test_login_invalid_credentials_shows_error_message(self, page: Page, user: str):
        """
        Verify that submitting an incorrect password displays the expected error message.
        Steps:
          1. Navigate to https://www.saucedemo.com/
          2. Enter credentials from test_data/credentials.json for the parametrized invalid user
          3. Click the login button
          4. Wait for the error element (data-test="error") to become visible
        Expected: The exact error text matches
          "Epic sadface: Username and password do not match any user in this service".
          The test fails loudly with a diff if the wording ever changes.
        """
        login_page = LoginPage(page)

        # 1. Navigate to the app
        login_page.navigate()

        # 2. Login with wrong password from test_data/credentials.json
        creds = _credentials[user]
        login_page.login(username=creds["username"], password=creds["password"])

        # 3. Wait for the error element to be visible
        login_page.error_message.wait_for(state="visible")

        # 4. Assert the exact error message text — test fails loudly if wording changes
        actual_error = login_page.error_message.inner_text().strip()
        assert actual_error == EXPECTED_INVALID_CREDENTIALS_ERROR, (
            f"Error message wording has changed!\n"
            f"  Expected: {EXPECTED_INVALID_CREDENTIALS_ERROR!r}\n"
            f"  Actual:   {actual_error!r}"
        )

    @pytest.mark.parametrize("user", ["error_user"], ids=["error_user"])
    def test_login_error_user_shows_error_button(self, page: Page, user: str):
        """
        Verify that logging in with the parametrized error user surfaces the
        error dismiss button on the page.
        Steps:
          1. Navigate to https://www.saucedemo.com/
          2. Enter credentials for the parametrized user (from test_data/credentials.json)
          3. Click the login button
          4. Wait for data-test="error-button" to become visible
        Expected: data-test="error-button" is visible, confirming the error state is shown.
        """
        login_page = LoginPage(page)

        # 1. Navigate to the app
        login_page.navigate()

        # 2. Login with user from test_data/credentials.json
        creds = _credentials[user]
        login_page.login(username=creds["username"], password=creds["password"])

        # 3. Assert the error-button element is visible
        login_page.error_button.wait_for(state="visible")
        assert login_page.error_button.is_visible(), (
            "data-test='error-button' should be visible after failed login with configured user"
        )
