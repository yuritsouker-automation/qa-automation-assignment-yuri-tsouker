import os

from playwright.sync_api import Page


class CartPage:
    URL_PATH = "/cart.html"
    DEFAULT_BASE_URL = "https://www.saucedemo.com"

    def __init__(self, page: Page, base_url: str | None = None):
        self.page = page
        self._base_url = (
            base_url
            or os.environ.get("UI_BASE_URL")
            or self.DEFAULT_BASE_URL
        ).rstrip("/")

        # ── Header ────────────────────────────────────────────────────────────
        self.header_container = page.locator('[data-test="header-container"]')
        self.shopping_cart_link = page.locator('[data-test="shopping-cart-link"]')
        self.shopping_cart_badge = page.locator('[data-test="shopping-cart-badge"]')

        # ── Burger menu ───────────────────────────────────────────────────────
        self.open_menu_button = page.locator('[data-test="open-menu"]')
        self.logout_link = page.locator('[data-test="logout-sidebar-link"]')

        # ── Page title ────────────────────────────────────────────────────────
        self.page_title = page.locator('[data-test="title"]')

        # ── Cart contents ─────────────────────────────────────────────────────
        self.cart_contents_container = page.locator('[data-test="cart-contents-container"]')
        self.cart_list = page.locator('[data-test="cart-list"]')
        self.cart_items = page.locator('[data-test="inventory-item"]')
        self.item_quantities = page.locator('[data-test="item-quantity"]')
        self.item_names = page.locator('[data-test="inventory-item-name"]')
        self.item_prices = page.locator('[data-test="inventory-item-price"]')

        # ── Action buttons ────────────────────────────────────────────────────
        self.continue_shopping_button = page.locator('[data-test="continue-shopping"]')
        self.checkout_button = page.locator('[data-test="checkout"]')

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate(self):
        """Go directly to the cart page URL."""
        self.page.goto(f"{self._base_url}{self.URL_PATH}")

    def wait_for_page_load(self):
        """Wait until the cart list is visible."""
        self.cart_list.wait_for(state="visible")

    def open_if_needed(self):
        """Open cart page from header link when not already on cart, then wait for load."""
        if "cart.html" not in self.page.url:
            self.shopping_cart_link.click()
        self.wait_for_page_load()

    # ── Cart badge ────────────────────────────────────────────────────────────

    def get_cart_badge_count(self) -> int:
        """Return the number shown on the cart badge (0 if badge is absent)."""
        if self.shopping_cart_badge.is_visible():
            return int(self.shopping_cart_badge.inner_text().strip())
        return 0

    # ── Cart item helpers ─────────────────────────────────────────────────────

    def get_item_count(self) -> int:
        """Return the number of distinct line items in the cart."""
        return self.cart_items.count()

    def get_item_names(self) -> list[str]:
        """Return the name of every item in the cart."""
        return [
            self.item_names.nth(i).inner_text().strip()
            for i in range(self.item_names.count())
        ]

    def get_item_prices(self) -> list[float]:
        """Return the price of every item in the cart as a float."""
        return [
            float(self.item_prices.nth(i).inner_text().strip().replace("$", ""))
            for i in range(self.item_prices.count())
        ]

    def get_cart_contents(self) -> list[dict]:
        """Return a list of dicts with 'name' and 'price' for each cart item."""
        return [
            {
                "name": self.item_names.nth(i).inner_text().strip(),
                "price": float(self.item_prices.nth(i).inner_text().strip().replace("$", "")),
            }
            for i in range(self.item_names.count())
        ]

    @staticmethod
    def _to_item_slug(item_name: str) -> str:
        """Convert a visible product name into SauceDemo's data-test slug format."""
        return (
            item_name.lower()
            .replace(" ", "-")
            .replace("(", "")
            .replace(")", "")
        )

    def get_remove_button(self, item_name: str):
        """Return the dynamic remove button locator for a cart item by visible name."""
        slug = self._to_item_slug(item_name)
        return self.page.locator(f'[data-test="remove-{slug}"]')

    def remove_item(self, item_name: str):
        """Click remove for a cart item by visible name."""
        self.get_remove_button(item_name).click()

    def clean_items(self, item_names: list[str]):
        """Remove all provided item names from the cart."""
        for item_name in item_names:
            self.remove_item(item_name)

    def start_checkout(self):
        """Proceed from cart to checkout step one."""
        self.checkout_button.click()

