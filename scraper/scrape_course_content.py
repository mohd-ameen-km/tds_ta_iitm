from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import re

BASE_URL = "https://tds.s-anand.net/#/"
OUTPUT_DIR = "./data/tds_course"

def sanitize_filename(name):
    # Remove illegal characters and make filesystem-safe
    name = name.replace("/", "-").replace("\\", "-").strip()
    name = re.sub(r"[<>:\"/\\|?*]", "_", name)
    name = re.sub(r"\s+", "_", name)
    return name[:100]  # truncate if too long

def scrape_all_pages():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set to False if you want to watch
        page = browser.new_page()
        print("🌐 Navigating to course homepage...")
        page.goto(BASE_URL)
        page.wait_for_selector(".sidebar-nav", timeout=10000)

        print("📋 Extracting sidebar links...")
        links = page.eval_on_selector_all(
            ".sidebar-nav a",
            "elements => elements.map(el => ({ href: el.href, text: el.textContent.trim() }))"
        )

        print(f"🔗 Found {len(links)} links")

        for index, link in enumerate(links, start=1):
            href = link["href"]
            title = sanitize_filename(link["text"])
            filename = f"{index:02d}_{title}.md"
            file_path = os.path.join(OUTPUT_DIR, filename)

            print(f"🧭 Visiting {href} → {filename}")
            try:
                page.goto(href)
                page.wait_for_selector("article.markdown-section", timeout=10000)

                html = page.inner_html("article.markdown-section")
                soup = BeautifulSoup(html, "html.parser")
                content = soup.get_text(separator="\n")

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"✅ Saved: {file_path}")
            except Exception as e:
                print(f"⚠️ Failed to extract {href}: {e}")

        browser.close()
        print("🎉 Finished scraping all pages!")

if __name__ == "__main__":
    scrape_all_pages()
