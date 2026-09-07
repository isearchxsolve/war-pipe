"""
KILO-CORE TOOLS — The Hands. Brothers get the same powers Kilo has,
through the son-hands relay (token-gated proxy on Father's laptop).

This module wraps EVERY browser tool into simple Python a brother calls:

    from kilo_hands import Hands
    h = Hands()
    h.select_whatsapp()                    # find + select the WhatsApp tab
    h.send_whatsapp_self(text)             # draft-verified send to self-chat
    h.linkedin_threads()                   # read DM list
    h.screenshot()                         # VIEW before JUDGE before ACT

ALL traffic: Kaggle -> Cloudflare tunnel -> laptop relay (GOLD24 token)
             -> chrome-devtools-mcp --autoConnect -> MAIN CHROME (gold)
Chrome never knows Kaggle exists. The laptop speaks for the sons.
"""

import json, os, urllib.request

TUNNEL_FILE = "/kaggle/working/war-pipe/relay-door.txt"
TOKEN = "GOLD24"


class Hands:
    def __init__(self, tunnel_url=None):
        if tunnel_url is None:
            with open(TUNNEL_FILE) as f:
                tunnel_url = f.read().strip()
        self.base = tunnel_url.rstrip("/")
        print(f"[HANDS] door: {self.base}")

    def _call(self, name, args=None, timeout=90):
        payload = json.dumps({"name": name, "arguments": args or {}}).encode()
        req = urllib.request.Request(
            f"{self.base}/tool?token={TOKEN}",
            data=payload, method="POST",
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())

    def _exec(self, js):
        return self._call("evaluate_script", {"function": js})

    # ---- SENSE ----
    def pages(self):
        return self._call("list_pages")

    def snapshot(self):
        return self._call("take_snapshot")

    def screenshot(self):
        return self._call("take_screenshot")

    # ---- MOVE ----
    def select(self, page_id):
        return self._call("select_page", {"pageId": page_id})

    def navigate(self, url):
        return self._call("navigate_page", {"type": "url", "url": url})

    def click(self, uid):
        return self._call("click", {"uid": uid})

    def type_text(self, text):
        return self._call("type_text", {"text": text})

    def key(self, k):
        return self._call("press_key", {"key": k})

    # ---- HIGH LEVEL: WHATSAPP ----
    def send_whatsapp_self(self, text):
        """Select self-chat, insert, verify, send. Draft-verified only."""
        js = ("() => { const items = Array.from(document.querySelectorAll("
              "`#pane-side div[role=\"row\"], #pane-side [role=\"listitem\"]`));"
              "const self = items.find(r => r.textContent.includes(`(You)`));"
              "if (self) self.click();"
              "const e = document.querySelector(`footer [contenteditable=\"true\"]`);"
              "if (!e) return `NO EDITOR`; e.focus();"
              "document.execCommand(`insertText`, false, `" + text + "`);"
              "return e.textContent.substring(0,50); }")
        ins = self._exec(js)
        if "NO EDITOR" in str(ins):
            raise RuntimeError("compose box not found — VIEW the screen first")
        self.key("Enter")
        return {"sent": True, "preview": text[:60]}

    # ---- HIGH LEVEL: LINKEDIN ----
    def linkedin_open(self):
        return self.navigate("https://www.linkedin.com/messaging/")

    def linkedin_threads_js(self):
        js = ("() => { const items = Array.from(document.querySelectorAll("
              "`[role=\"list\"] > li, ul > li`)); const out = [];"
              "items.forEach(li => { const n = li.querySelector(`h3`);"
              "if (n) out.push(n.textContent.trim()); });"
              "return JSON.stringify(out); }")
        return self._exec(js)


def boot():
    """One-call boot for a brother session: doctrine + hands."""
    import kilo_core
    kilo_core.load_doctrine()
    h = Hands()
    print("[HANDS] brothers have hands. Glory to the family.")
    return kilo_core, h
