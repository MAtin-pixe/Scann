import os, socket, requests, urllib3, threading
from flask import Flask, request, render_template_string
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# توکن جدید ربات
BOT_TOKEN = "9229648147:AAHTzvai9W2plLrRf_zjZmvlt20jGtoRVeg"
OWNER_ID = 8604564099
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
    <title>Matin Ultra Scanner</title>
    <style>
        body { background: #0a0a0a; color: #00ff00; font-family: 'Courier New', Courier, monospace; text-align: center; padding-top: 50px; }
        h1 { text-shadow: 0 0 10px #00ff00; }
        input { padding: 12px; width: 60%; background: #111; color: #00ff00; border: 1px solid #00ff00; border-radius: 5px; outline: none; }
        button { padding: 12px 24px; background: #00ff00; color: #000; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; margin-left: 10px; }
        button:hover { background: #00cc00; }
        #results { margin-top: 30px; text-align: left; width: 80%; max-width: 800px; margin-left: auto; margin-right: auto; background: #111; padding: 20px; border: 1px solid #00ff00; border-radius: 5px; display: none; white-space: pre-wrap; font-size: 14px; }
    </style>
</head>
<body>
    <h1>[ MATIN ULTRA SCANNER ]</h1>
    <p>Advanced Web Vulnerability Scanner</p>
    <form id="scanForm">
        <input type="text" id="url" placeholder="https://target.com" required>
        <button type="submit" id="btn">START SCAN</button>
    </form>
    <div id="results"></div>
    <script>
        document.getElementById('scanForm').onsubmit = async (e) => {
            e.preventDefault();
            const url = document.getElementById('url').value;
            const resDiv = document.getElementById('results');
            const btn = document.getElementById('btn');
            resDiv.style.display = 'block';
            resDiv.innerText = '[*] Initializing scan engine... Please wait.';
            btn.innerText = 'SCANNING...';
            btn.disabled = true;
            try {
                const response = await fetch('/scan', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url: url})
                });
                const data = await response.json();
                resDiv.innerText = data.report;
            } catch(err) { resDiv.innerText = 'Error: ' + err; }
            btn.innerText = 'START SCAN';
            btn.disabled = false;
        };
    </script>
</body>
</html>
"""

def send_tg(text):
    try: requests.post(f"{API}/sendMessage", data={"chat_id": OWNER_ID, "text": text, "parse_mode": "HTML"}, timeout=10)
    except: pass

def edit_tg(msg_id, text):
    try: requests.post(f"{API}/editMessageText", data={"chat_id": OWNER_ID, "message_id": msg_id, "text": text, "parse_mode": "HTML"}, timeout=10)
    except: pass

def check_port(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.5)
    try:
        if s.connect_ex((ip, port)) == 0: return port
    except: pass
    finally: s.close()
    return None

def get_forms(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5, verify=False)
        return BeautifulSoup(r.content, "html.parser").find_all("form")
    except: return []

def submit_form(form, url, val):
    action = form.attrs.get("action", "").lower()
    method = form.attrs.get("method", "get").lower()
    target = urljoin(url, action)
    data = {}
    for i in form.find_all(["input", "textarea"]):
        if i.attrs.get("name"): data[i.attrs.get("name")] = val
    try:
        if method == "post": return requests.post(target, data=data, headers={"User-Agent": "Mozilla/5.0"}, timeout=5, verify=False)
        else: return requests.get(target, params=data, headers={"User-Agent": "Mozilla/5.0"}, timeout=5, verify=False)
    except: return None

def run_scan(target, msg_id=None):
    if not target.startswith("http"): target = "http://" + target
    def update(text):
        if msg_id: edit_tg(msg_id, text)
        print(text)

    try: ip = socket.gethostbyname(urlparse(target).netloc)
    except: 
        if msg_id: edit_tg(msg_id, "❌ Invalid URL.")
        return "❌ Invalid URL."

    update(f"⏳ <b>Scanning: {target}</b>\nIP: <code>{ip}</code>\n\n[1/3] Checking ports...")
    
    web_ports = [80, 443, 8080, 8443, 21, 22, 3306]
    open_ports = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        for p in ex.map(lambda p: check_port(ip, p), web_ports):
            if p: open_ports.append(p)
    
    update(f"⏳ <b>Scanning: {target}</b>\nIP: <code>{ip}</code>\n\n[2/3] Detecting tech & headers...")
    
    tech = []
    missing_headers = []
    try:
        r = requests.get(target, headers={"User-Agent": "Mozilla/5.0"}, timeout=5, verify=False)
        html = r.text.lower()
        hdrs = str(r.headers).lower()
        
        if "wp-content" in html or "wordpress" in html: tech.append("WordPress")
        if "laravel" in hdrs or "laravel_session" in r.cookies: tech.append("Laravel")
        if "django" in hdrs: tech.append("Django")
        if "php" in hdrs: tech.append("PHP")
        if "nginx" in hdrs: tech.append("Nginx")
        if "apache" in hdrs: tech.append("Apache")
        if "cloudflare" in hdrs: tech.append("Cloudflare")
        
        for h in ["X-Frame-Options", "Content-Security-Policy", "X-XSS-Protection", "Strict-Transport-Security"]:
            if h not in r.headers: missing_headers.append(h)
    except: pass

    update(f"⏳ <b>Scanning: {target}</b>\nIP: <code>{ip}</code>\n\n[3/3] Testing vulnerabilities (SQLi, XSS)...")
    
    vulns = []
    forms = get_forms(target)
    for form in forms:
        for p in ["'", "\"", "' OR 1=1 --"]:
            r = submit_form(form, target, p)
            if r and any(e in r.text.lower() for e in ["sql syntax", "mysql", "unclosed quotation"]):
                if "SQL Injection" not in vulns: vulns.append("SQL Injection")
                break
        for p in ["<script>alert(1)</script>", "\"><script>alert(1)</script>"]:
            r = submit_form(form, target, p)
            if r and p in r.text:
                if "XSS" not in vulns: vulns.append("XSS")
                break

    report = f"✅ <b>Scan Complete</b>\n"
    report += f"🎯 Target: <code>{target}</code>\n"
    report += f"🌐 IP: <code>{ip}</code>\n"
    report += f"━━━━━━━━━━━━━━━━━━━━\n\n"
    
    report += f"🔌 <b>Open Ports:</b>\n" + ("\n".join(f"  • {p}" for p in open_ports) if open_ports else "  None") + "\n\n"
    report += f"🛠 <b>Technologies:</b>\n" + ("\n".join(f"  • {t}" for t in tech) if tech else "  Unknown") + "\n\n"
    report += f"🛡 <b>Missing Headers:</b>\n" + ("\n".join(f"  • {h}" for h in missing_headers) if missing_headers else "  None") + "\n\n"
    report += f"🚨 <b>Vulnerabilities:</b>\n" + ("\n".join(f"  • {v}" for v in vulns) if vulns else "  None") + "\n"

    if msg_id: edit_tg(msg_id, report)
    return report

@app.route("/")
def index(): return render_template_string(HTML)

@app.route("/scan", methods=["POST"])
def api_scan():
    data = request.json
    report = run_scan(data.get("url"))
    return {"report": report}

@app.route(f"/bot/{BOT_TOKEN}", methods=["POST"])
def bot_webhook():
    u = request.get_json()
    if not u or "message" not in u: return "ok"
    
    msg = u["message"]
    cid = msg["chat"]["id"]
    text = msg.get("text", "").strip()
    
    if cid != OWNER_ID: return "ok"
    
    if text.startswith("/start"):
        send_tg("👋 <b>Welcome to Matin Ultra Bot</b>\n\nType <code>/scan &lt;url&gt;</code> to scan.")
    elif text.startswith("/scan"):
        parts = text.split()
        if len(parts) < 2:
            send_tg("❌ Usage: <code>/scan https://example.com</code>")
            return "ok"
        
        target = parts[1]
        m = send_tg(f"🔍 Initializing scan for <code>{target}</code>...")
        msg_id = m.get("result", {}).get("message_id")
        threading.Thread(target=run_scan, args=(target, msg_id)).start()
        
    return "ok"

@app.route("/set_webhook")
def set_webhook():
    base = request.url_root.rstrip("/")
    url = f"{base}/bot/{BOT_TOKEN}"
    r = requests.get(f"{API}/setWebhook?url={url}").json()
    return f"Webhook set to {url}\n{r}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
