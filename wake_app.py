from playwright.sync_api import sync_playwright

APP_URL = "https://charlottekwon-portfolio-pulse.streamlit.app/"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"Opening {APP_URL}")
        page.goto(APP_URL, wait_until="domcontentloaded", timeout=120_000)
        wake_button = page.get_by_text("Yes, get this app back up!", exact=False)
        if wake_button.count() > 0:
            print("Sleeping page detected. Clicking wake button...")
            wake_button.first.click()
            page.wait_for_timeout(20_000)
            print("Wake request sent.")
        else:
            print("No sleeping-page button detected; app appears awake.")
        print(f"Final URL: {page.url}")
        browser.close()

if __name__ == "__main__":
    main()
