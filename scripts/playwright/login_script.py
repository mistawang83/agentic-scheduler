from playwright.sync_api import sync_playwright
import os

STATE_FILE = "storage/playwright_auth.json"

if not os.path.exists("storage"):
    os.makedirs("storage")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Go to your Brightspace login page
    page.goto("https://mycourses2.mcgill.ca/d2l/home")

    print("Please log in manually, then come back here.")
    print("After you see your Brightspace dashboard, press ENTER.")
    input()

    # Save authenticated session
    context.storage_state(path=STATE_FILE)

    print(f"Storage state saved to {STATE_FILE}")
    browser.close()
