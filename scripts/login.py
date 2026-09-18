"""Log in to Brightspace manually and save the session for the fetcher agent.

Run: uv run scripts/login.py
"""
from playwright.sync_api import sync_playwright

from agentic_scheduler.config import AUTH_STATE_FILE, BRIGHTSPACE_BASE_URL

AUTH_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Go to your Brightspace login page
    page.goto(f"{BRIGHTSPACE_BASE_URL}/d2l/home")

    print("Please log in manually, then come back here.")
    print("After you see your Brightspace dashboard, press ENTER.")
    input()

    # Save authenticated session
    context.storage_state(path=AUTH_STATE_FILE)

    print(f"Storage state saved to {AUTH_STATE_FILE}")
    browser.close()
