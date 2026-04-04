from playwright.sync_api import sync_playwright
import json
from urllib.parse import urljoin
from datetime import datetime

URL = "https://www.caluniv.ac.in/news/news.html"
BASE_URL = "https://www.caluniv.ac.in/"

def scrape_notices():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()

        page.goto(URL, timeout=60000)
        page.wait_for_load_state("networkidle")

        # Inspect page: notices are usually inside table rows
        rows = page.query_selector_all("table tr")

        notices = []

        for row in rows:
            cols = row.query_selector_all("td")

            if len(cols) < 2:
                continue

            date_text = cols[0].inner_text().strip()
            link_tag = cols[1].query_selector("a")

            if not link_tag:
                continue

            title = link_tag.inner_text().strip()
            link = link_tag.get_attribute("href")

            if not title or not link:
                continue

            full_url = urljoin(BASE_URL, link)

            notices.append({
                "title": title,
                "url": full_url,
                "date": date_text,
                "type": "pdf" if full_url.endswith(".pdf") else "web",
                "source": "calcutta_university"
            })

        browser.close()

        output = {
            "source": "calcutta_university",
            "scraped_at": datetime.utcnow().isoformat(),
            "total": len(notices),
            "notices": notices
        }

        # Save JSON
        with open("notices.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"Scraped {len(notices)} notices")

scrape_notices()