import json
import os

import pytest
from playwright.sync_api import Page

from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "test_data", "credentials.json")
PRODUCTS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "test_data", "products.json")

with open(CREDENTIALS_PATH) as f:
    _credentials = json.load(f)

with open(PRODUCTS_PATH) as f:
    _products = json.load(f)


class TestCart:
    @pytest.mark.parametrize(
        "products_to_add",
        [_products["add_to_cart_two_items"]],
        ids=["add_to_cart_two_items"],
    )
    def test_add_two_products_to_cart_and_verify_contents(self, page: Page, products_to_add: list[dict]):
        """
        Verify that adding products to the cart is reflected correctly in the badge and cart contents.
        """
        login_page = LoginPage(page)
        login_page.navigate()
        creds = _credentials["standard_user"]
        login_page.login(username=creds["username"], password=creds["password"])

        inventory_page = InventoryPage(page)
        inventory_page.wait_for_page_load()

        for product in products_to_add:
            inventory_page.add_item_to_cart(product["name"])

        try:
            badge_count = inventory_page.get_cart_badge_count()
            assert badge_count == len(products_to_add), (
                f"Cart badge should show {len(products_to_add)}, got {badge_count}"
            )

            inventory_page.shopping_cart_link.click()
            cart_page = CartPage(page)
            cart_page.wait_for_page_load()

            assert cart_page.get_item_count() == len(products_to_add), (
                f"Cart should contain {len(products_to_add)} items, got {cart_page.get_item_count()}"
            )
            assert cart_page.get_cart_badge_count() == len(products_to_add), (
                f"Cart badge on cart page should show {len(products_to_add)}, "
                f"got {cart_page.get_cart_badge_count()}"
            )

            cart_contents = cart_page.get_cart_contents()
            cart_by_name = {item["name"]: item["price"] for item in cart_contents}

            for expected in products_to_add:
                assert expected["name"] in cart_by_name, (
                    f"Expected product '{expected['name']}' not found in cart. "
                    f"Cart contains: {list(cart_by_name.keys())}"
                )
                assert cart_by_name[expected["name"]] == expected["price"], (
                    f"Price mismatch for '{expected['name']}': "
                    f"expected ${expected['price']}, got ${cart_by_name[expected['name']]}"
                )
        finally:
            cleanup_cart_page = CartPage(page)
            cleanup_cart_page.open_if_needed()
            cleanup_cart_page.clean_items([product["name"] for product in products_to_add])
            login_page.logout()


