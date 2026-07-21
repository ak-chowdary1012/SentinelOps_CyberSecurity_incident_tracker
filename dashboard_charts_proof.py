import http.server
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path
from urllib.request import urlopen

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend" / "pages"
SCREENSHOT = ROOT / "dashboard_charts_proof.png"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002
        return


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def wait_for(url: str, timeout: float = 15.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=1) as response:
                if response.status < 500:
                    return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError(f"Timed out waiting for {url}")


def main() -> None:
    api = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=BACKEND,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    httpd = ReusableTCPServer(("127.0.0.1", 5500), lambda *args, **kwargs: QuietHandler(*args, directory=FRONTEND, **kwargs))
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    try:
        wait_for("http://127.0.0.1:8000/health")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            console_errors: list[str] = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.goto("http://127.0.0.1:5500/dashboard.html", wait_until="networkidle")
            page.fill("#loginUsername", "admin")
            page.fill("#loginPassword", "AdminPass123!")
            page.click("button[type='submit']")
            page.wait_for_selector("canvas", timeout=5000)
            page.wait_for_function(
                """() => [...document.querySelectorAll('canvas')].length > 0
                    && [...document.querySelectorAll('canvas')].every((canvas) => {
                        const ctx = canvas.getContext('2d');
                        const {data} = ctx.getImageData(0, 0, canvas.width, canvas.height);
                        let painted = 0;
                        for (let i = 3; i < data.length; i += 4) {
                            if (data[i] > 0) painted++;
                        }
                        return painted > 500;
                    })""",
                timeout=10000,
            )
            canvas_count = page.eval_on_selector_all("canvas", "els => els.length")
            painted_pixels = page.eval_on_selector_all(
                "canvas",
                """els => els.map((canvas) => {
                    const ctx = canvas.getContext('2d');
                    const {data} = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    let painted = 0;
                    for (let i = 3; i < data.length; i += 4) {
                        if (data[i] > 0) painted++;
                    }
                    return painted;
                })""",
            )
            token_present = page.evaluate("Boolean(localStorage.getItem('sentinelops_access_token'))")
            page.screenshot(path=str(SCREENSHOT), full_page=True)
            browser.close()
        print(f"browser login: ok, token present: {token_present}")
        print(f"canvas count: {canvas_count}")
        print(f"canvas painted pixels: {painted_pixels}")
        print(f"console errors: {console_errors}")
        print(f"screenshot: {SCREENSHOT}")
        assert token_present, "login token missing"
        assert canvas_count > 0, "no chart canvases rendered"
        assert all(count > 500 for count in painted_pixels), "one or more chart canvases are blank"
        assert console_errors == [], f"console errors present: {console_errors}"
    finally:
        httpd.shutdown()
        httpd.server_close()
        api.terminate()
        try:
            api.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api.kill()


if __name__ == "__main__":
    main()
