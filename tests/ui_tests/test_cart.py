import json
import os

import pytest
from playwright.sync_api import Page

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage

PRODUCTS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "test_data", "products.json")

with open(PRODUCTS_PATH) as f:
    _products = json.load(f)


@pytest.mark.usefixtures("logout_after_test")
class TestCart:

    @pytest.mark.parametrize(
        "products_to_add",
        [_products["add_to_cart_two_items"]],
        ids=["add_to_cart_two_items"],
    )
    def test_add_two_products_to_cart_and_verify_contents(
        self,
        page: Page,
        products_to_add: list[dict],
        login_as_user,
    ):
        """
        Verify that adding products to the cart is reflected correctly in the badge and cart contents.
        """
        # 1. Login with standard_user
        login_as_user("standard_user")

        # 2. Wait for inventory page and add configured products to cart
        inventory_page = InventoryPage(page)
        inventory_page.wait_for_page_load()

        for product in products_to_add:
            inventory_page.add_item_to_cart(product["name"])

        try:
            # 3. Verify cart badge count on inventory page
            badge_count = inventory_page.get_cart_badge_count()
            assert badge_count == len(products_to_add), (
                f"Cart badge should show {len(products_to_add)}, got {badge_count}"
            )

            # 4. Open cart and validate item/badge counts
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

            # 5. Validate expected names and prices in cart contents
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
            # 6. Cleanup cart items to keep the next tests isolated
            cleanup_cart_page = CartPage(page)
            cleanup_cart_page.open_if_needed()
            cleanup_cart_page.clean_items([product["name"] for product in products_to_add])

    @pytest.mark.parametrize(
        "checkout_info",
        [_products["checkout_user_info"]],
        ids=["checkout_user_info"],
    )
    def test_end_to_end_checkout_with_visual_user(self, page: Page, checkout_info: dict, login_as_user):
        """
        End-to-end checkout with visual_user:
        Add a product, go through checkout (Your Information → Overview → Finish),
        and verify the order-complete confirmation.
        """
        checkout_product = _products["checkout_single_item"]
        # 1. Login with visual_user
        login_as_user("visual_user")

        # 2. Add the configured product from inventory
        inventory_page = InventoryPage(page)
        inventory_page.wait_for_page_load()
        inventory_page.add_item_to_cart(checkout_product["name"])

        cart_page = CartPage(page)
        checkout_page = CheckoutPage(page)

        # 3. Start checkout from cart page
        cart_page.open_if_needed()
        cart_page.start_checkout()

        # 4. Complete information step and continue
        checkout_page.wait_for_information_step()
        checkout_page.fill_information(**checkout_info)
        checkout_page.continue_to_overview()

        # 5. Finish checkout from overview
        checkout_page.wait_for_overview_step()
        checkout_page.finish_checkout()

        # 6. Verify checkout completion state and confirmation message
        checkout_page.wait_for_complete_step()
        assert checkout_page.checkout_complete_container.is_visible(), (
            "Checkout complete container should be visible after finish"
        )
        assert checkout_page.get_complete_header_text() == "Thank you for your order!", (
            "Order completion confirmation text changed unexpectedly"
        )

    @pytest.mark.parametrize(
        "products_to_add",
        [_products["add_to_cart_two_items"]],
        ids=["add_to_cart_two_items"],
    )
    def test_sort_price_low_to_high_with_performance_glitch_user(
        self,
        page: Page,
        products_to_add: list[dict],
        login_as_user,
    ):
        """
        Test product sorting by price low-to-high and cart badge updates
        while logged in as performance_glitch_user.
        Steps:
          1. Login with performance_glitch_user
          2. Sort products by price low-to-high
          3. Verify prices are in ascending order
          4. Add products one-by-one and verify cart badge increments
          5. Navigate to cart and remove products one-by-one, verify badge decrements
        """
        # 1. Login with performance_glitch_user
        login_as_user("performance_glitch_user")

        # 2. Wait for inventory page and apply low-to-high sort
        inventory_page = InventoryPage(page)
        inventory_page.wait_for_page_load()

        inventory_page.sort_by(InventoryPage.SORT_PRICE_LOW_HIGH)

        # 3. Verify prices are sorted in ascending order
        prices = inventory_page.get_item_prices()
        assert prices == sorted(prices), (
            f"Expected prices to be sorted low-to-high, got {prices}"
        )

        # 4. Add items and validate badge increments after each add
        for expected_badge_count, product in enumerate(products_to_add, start=1):
            inventory_page.add_item_to_cart(product["name"])
            assert inventory_page.get_cart_badge_count() == expected_badge_count, (
                f"Cart badge should be {expected_badge_count} after adding '{product['name']}'"
            )

        # 5. Open cart page and remove items while validating badge decrements
        cart_page = CartPage(page)
        cart_page.open_if_needed()

        for expected_badge_count, product in zip(
            range(len(products_to_add) - 1, -1, -1),
            products_to_add,
        ):
            cart_page.remove_item(product["name"])
            assert cart_page.get_cart_badge_count() == expected_badge_count, (
                f"Cart badge should be {expected_badge_count} after removing '{product['name']}'"
            )


