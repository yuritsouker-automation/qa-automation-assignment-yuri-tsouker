from playwright.sync_api import Page, Locator


class InventoryPage:
    URL = "https://www.saucedemo.com/inventory.html"

    # Sort options exposed as constants for use in tests
    SORT_NAME_A_Z = "az"
    SORT_NAME_Z_A = "za"
    SORT_PRICE_LOW_HIGH = "lohi"
    SORT_PRICE_HIGH_LOW = "hilo"

    def __init__(self, page: Page):
        self.page = page

        # ── Header ────────────────────────────────────────────────────────────
        self.header_container = page.locator('[data-test="header-container"]')
        self.primary_header = page.locator('[data-test="primary-header"]')
        self.shopping_cart_link = page.locator('[data-test="shopping-cart-link"]')

        # ── Burger menu ───────────────────────────────────────────────────────
        self.open_menu_button = page.locator('[data-test="open-menu"]')
        self.close_menu_button = page.locator('[data-test="close-menu"]')
        self.sidebar_all_items_link = page.locator('[data-test="inventory-sidebar-link"]')
        self.sidebar_about_link = page.locator('[data-test="about-sidebar-link"]')
        self.sidebar_logout_link = page.locator('[data-test="logout-sidebar-link"]')
        self.sidebar_reset_link = page.locator('[data-test="reset-sidebar-link"]')

        # ── Secondary header / toolbar ────────────────────────────────────────
        self.secondary_header = page.locator('[data-test="secondary-header"]')
        self.page_title = page.locator('[data-test="title"]')
        self.sort_dropdown = page.locator('[data-test="product-sort-container"]')
        self.active_sort_option = page.locator('[data-test="active-option"]')

        # ── Product list ──────────────────────────────────────────────────────
        self.inventory_container = page.locator('[data-test="inventory-container"]')
        self.inventory_list = page.locator('[data-test="inventory-list"]')
        self.inventory_items = page.locator('[data-test="inventory-item"]')

        # Per-item sub-locators (call .nth(index) on these)
        self.item_names = page.locator('[data-test="inventory-item-name"]')
        self.item_descriptions = page.locator('[data-test="inventory-item-desc"]')
        self.item_prices = page.locator('[data-test="inventory-item-price"]')

        # ── Footer ────────────────────────────────────────────────────────────
        self.footer = page.locator('[data-test="footer"]')
        self.footer_copy = page.locator('[data-test="footer-copy"]')
        self.social_twitter = page.locator('[data-test="social-twitter"]')
        self.social_facebook = page.locator('[data-test="social-facebook"]')
        self.social_linkedin = page.locator('[data-test="social-linkedin"]')

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate(self):
        """Go directly to the inventory page URL."""
        self.page.goto(self.URL)

    def wait_for_page_load(self):
        """Wait until the product list is visible."""
        self.inventory_list.wait_for(state="visible")

    # ── Burger menu ───────────────────────────────────────────────────────────

    def open_menu(self):
        self.open_menu_button.click()

    def close_menu(self):
        self.close_menu_button.click()

    def logout(self):
        self.open_menu()
        self.sidebar_logout_link.click()

    def reset_app_state(self):
        self.open_menu()
        self.sidebar_reset_link.click()
        self.close_menu()

    # ── Sorting ───────────────────────────────────────────────────────────────

    def sort_by(self, option: str):
        """Sort products. Use InventoryPage.SORT_* constants."""
        self.sort_dropdown.select_option(option)

    def get_active_sort_option(self) -> str:
        return self.active_sort_option.inner_text().strip()

    # ── Product helpers ───────────────────────────────────────────────────────

    def get_item_count(self) -> int:
        """Return the number of product cards currently displayed."""
        return self.inventory_items.count()

    def get_item_names(self) -> list[str]:
        """Return the visible name of every product card."""
        return [
            self.item_names.nth(i).inner_text().strip()
            for i in range(self.item_names.count())
        ]

    def get_item_prices(self) -> list[float]:
        """Return the price of every product card as a float."""
        return [
            float(self.item_prices.nth(i).inner_text().strip().replace("$", ""))
            for i in range(self.item_prices.count())
        ]

    def get_add_to_cart_button(self, item_name: str) -> Locator:
        """Return the 'Add to cart' button locator for a product by its visible name."""
        slug = item_name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace(".", "")
        return self.page.locator(f'[data-test="add-to-cart-{slug}"]')

    def add_item_to_cart(self, item_name: str):
        """Click 'Add to cart' for the product with the given visible name."""
        self.get_add_to_cart_button(item_name).click()

    def get_cart_badge_count(self) -> int:
        """Return the number shown on the shopping-cart badge (0 if no badge)."""
        badge = self.page.locator('.shopping_cart_badge')
        if badge.is_visible():
            return int(badge.inner_text().strip())
        return 0

