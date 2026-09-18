"""Open Brightspace with the saved session to check that the login still works.

Run: uv run scripts/check_login.py
"""
from playwright.sync_api import sync_playwright

from agentic_scheduler.config import AUTH_STATE_FILE, BRIGHTSPACE_BASE_URL

with sync_playwright() as p:
    # Launch browser (headless=False so you can see it)
    browser = p.chromium.launch(headless=False)

    # Load the storage state
    context = browser.new_context(storage_state=AUTH_STATE_FILE)

    page = context.new_page()

    # Go to Brightspace homepage
    page.goto(f"{BRIGHTSPACE_BASE_URL}/d2l/home")

    # Wait a few seconds to observe
    page.wait_for_timeout(5000)  # 5 seconds

    # Print page title to verify login
    print("Page title:", page.title())

    browser.close()
