from playwright.sync_api import sync_playwright

STATE_FILE = "playwright/brightspace_state.json"

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
