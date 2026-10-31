import os, socket, requests, urllib3, threading
from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BOT_TOKEN = "9229648147:AAHTzvai9W2plLrRf_zjZmvlt20jGtoRVeg"
OWNER_ID = 8604564099
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__)

HTML = """
<!doctype html><html><head><title>Matin Scanner</title><style>body { background: #111; color: #0f0; text-align: center; padding-top: 50px; } input { padding: 10px; } button { padding: 10px; }</style></head>
<body><h1>Scanner Ready</h1><p>Bot is running.</p></body></html>
"""

@app.route("/")
def index(): return render_template_string(HTML)

@app.route("/set_webhook")
def set_webhook():
    base = request.url_root.rstrip("/")
    url = f"{base}/api/bot/{BOT_TOKEN}"
    r = requests.get(f"{API}/setWebhook?url={url}").json()
    return f"Webhook set to {url}\n{r}"

@app.route(f"/api/bot/{BOT_TOKEN}", methods=["POST"])
def bot_webhook():
    u = request.get_json()
    if not u or "message" not in u: return "ok"
    msg = u["message"]
    cid = msg["chat"]["id"]
    text = msg.get("text", "").strip()
    if cid != OWNER_ID: return "ok"
    
    if text.startswith("/start"):
        requests.post(f"{API}/sendMessage", data={"chat_id": OWNER_ID, "text": "ربات با موفقیت به Vercel وصل شد!"})
    return "ok"
