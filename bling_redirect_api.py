import sys
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CaptureRequest(BaseModel):
    login_url: str
    target_url: str
    username: str
    password: str

app = FastAPI()

@app.post("/capture-redirect")
def capture_redirect(req: CaptureRequest):
    last_html = ""
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=True,
                args=["--no-sandbox","--disable-dev-shm-usage"]
            )
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/115.0.0.0 Safari/537.36"
                )
            )
            page = context.new_page()

            page.goto(req.login_url, timeout=45000)
            page.wait_for_load_state("networkidle", timeout=20000)
            last_html = page.content()

            page.wait_for_selector("#username", timeout=30000)
            page.wait_for_selector("input[data-gtm-form-interact-field-id=\"1\"]", timeout=30000)

            page.fill("#username", req.username)
            page.fill("input[data-gtm-form-interact-field-id=\"1\"]", req.password)

            with page.expect_navigation(timeout=30000):
                page.click("button.login-button-submit")

            page.wait_for_load_state("networkidle", timeout=20000)
            last_html = page.content()

            page.goto(req.target_url, timeout=45000)
            page.wait_for_load_state("networkidle", timeout=30000)
            final_url = page.url
            last_html = page.content()

            browser.close()
            return {"redirected_url": final_url}

    except PWTimeout as e:
        raise HTTPException(status_code=504, detail={"error":"Timeout","html": last_html[:5000]})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e), "html": last_html[:5000]})
