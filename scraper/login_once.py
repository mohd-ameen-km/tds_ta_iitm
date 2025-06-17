from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://discourse.onlinedegree.iitm.ac.in")
    input("⚠️ Please login manually, then press Enter here...")
    context.storage_state(path="auth.json")
    browser.close()
    print("✅ Login cookies saved to auth.json")
