from playwright.sync_api import Page


class CheckoutPage:
    def __init__(self, page: Page):
        self.page = page

        # Step One: Your Information
        self.first_name_input = page.locator('[data-test="firstName"]')
        self.last_name_input = page.locator('[data-test="lastName"]')
        self.postal_code_input = page.locator('[data-test="postalCode"]')
        self.continue_button = page.locator('[data-test="continue"]')

        # Step Two: Overview
        self.finish_button = page.locator('[data-test="finish"]')

        # Complete
        self.checkout_complete_container = page.locator('[data-test="checkout-complete-container"]')
        self.complete_header = page.locator('[data-test="complete-header"]')

    def wait_for_information_step(self):
        self.first_name_input.wait_for(state="visible")

    def fill_information(self, first_name: str, last_name: str, postal_code: str):
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.postal_code_input.fill(postal_code)

    def continue_to_overview(self):
        self.continue_button.click()

    def wait_for_overview_step(self):
        self.finish_button.wait_for(state="visible")

    def finish_checkout(self):
        self.finish_button.click()

    def wait_for_complete_step(self):
        self.complete_header.wait_for(state="visible")

    def get_complete_header_text(self) -> str:
        return self.complete_header.inner_text().strip()
