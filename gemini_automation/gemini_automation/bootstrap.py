import os
from playwright.sync_api import sync_playwright

def run_login_setup():
    user_session_path = os.path.join(os.getcwd(), "auth/user_data")

    with sync_playwright() as p:
        # We use 'launch' instead of 'launch_persistent_context' temporarily 
        # to ensure a clean slate, OR add these specific args:
        browser_context = p.chromium.launch_persistent_context(
            user_session_path,
            headless=False,
            # EXTREMELY IMPORTANT ARGS:
            args=[
                "--disable-blink-features=AutomationControlled", # Hides 'navigator.webdriver'
                "--use-fake-ui-for-media-stream",
                "--window-size=1920,1080"
            ],
            ignore_default_args=["--enable-automation"] # Removes the "Chrome is being controlled" bar
        )
        
        page = browser_context.new_page()
        
        # Set a realistic User Agent
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

        page.goto("https://accounts.google.com/") # Go to Google Account first, then Gemini
        
        print("\nACTION REQUIRED:")
        print("1. Log in to your Google Account.")
        print("2. Once signed in, go to https://gemini.google.com/")
        print("3. Close the browser manually after you see the chat box.")

        # Instead of wait_for_timeout
        print("Please log in, then click 'Resume' in the Playwright Inspector or close the browser.")
        page.pause()
        browser_context.close()

if __name__ == "__main__":
    run_login_setup()