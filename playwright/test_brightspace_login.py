from playwright.sync_api import sync_playwright

# Path to your storage state JSON
STORAGE_STATE = "./playwright/brightspace_state.json"

with sync_playwright() as p:
    # Launch browser (headless=False so you can see it)
    browser = p.chromium.launch(headless=False)

    # Load the storage state
    context = browser.new_context(storage_state=STORAGE_STATE)

    page = context.new_page()

    # Go to Brightspace homepage
    page.goto("https://mycourses2.mcgill.ca/d2l/home")

    # Wait a few seconds to observe
    page.wait_for_timeout(5000)  # 5 seconds

    # Optional: print page title to verify login
    print("Page title:", page.title())

    browser.close()
