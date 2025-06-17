from playwright.sync_api import sync_playwright

def save_auth():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Keep browser visible
        context = browser.new_context()
        page = context.new_page()

        # Open login page
        print("🌐 Opening login page...")
        page.goto("https://discourse.onlinedegree.iitm.ac.in/login")

        print("🔐 Please log in manually in the browser window.")
        page.wait_for_timeout(60000)  # Give you 60 seconds to log in

        # Save session
        context.storage_state(path="auth.json")
        print("✅ auth.json saved!")

        browser.close()

if __name__ == "__main__":
    save_auth()
