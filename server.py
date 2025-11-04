# server.py
import os
import tempfile
import base64
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from sbvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import signal

API_KEY = os.environ.get("API_KEY", "")  # configure no Render
CHROME_PATH = os.environ.get("CHROME_PATH", "/usr/bin/google-chrome-stable")

app = FastAPI(title="Simulador Web (sbvirtualdisplay + selenium)")

# Start a global Xvfb display so we reuse it across requests (optional)
display = None
try:
    display = Display(visible=0, size=(1366, 768))
    display.start()
    print("🟢 Xvfb iniciado (sbvirtualdisplay).")
except Exception as e:
    # fail fast — if Xvfb cannot start, raise error to detect on deploy
    print("⚠️ Não foi possível iniciar Xvfb:", e)
    raise

class SimRequest(BaseModel):
    url: str

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # headless moderno
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1366,768")
    # If chrome binary isn't in default path, set it:
    chrome_options.binary_location = CHROME_PATH
    # create driver (assumes chromedriver in PATH)
    driver = webdriver.Chrome(service=Service(), options=chrome_options)
    return driver

def check_auth(request: Request):
    if not API_KEY:
        return True  # dev: no auth required if API_KEY not set (but set in production!)
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
        return token == API_KEY
    return False

@app.post("/simulate")
async def simulate(req: SimRequest, request: Request):
    if not check_auth(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
    url = req.url
    if not url.lower().startswith(("http://","https://")):
        raise HTTPException(status_code=400, detail="URL inválida; inclua http:// ou https://")
    driver = None
    tmpfile = None
    try:
        driver = create_driver()
        driver.get(url)
        title = driver.title
        html = driver.page_source

        tmpfile = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        driver.save_screenshot(tmpfile.name)
        driver.quit()
        with open(tmpfile.name, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return {"status":"ok", "title": title, "html": html, "screenshot_base64": b64}
    except Exception as e:
        if driver:
            try:
                driver.quit()
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmpfile:
            try:
                os.unlink(tmpfile.name)
            except:
                pass

# Optional: graceful shutdown to stop Xvfb when container stops
def _shutdown(*args):
    global display
    print("Shutting down... stopping display")
    if display:
        try:
            display.stop()
        except:
            pass
    raise SystemExit()

signal.signal(signal.SIGTERM, _shutdown)
signal.signal(signal.SIGINT, _shutdown)
