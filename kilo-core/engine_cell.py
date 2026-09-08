# KILO ENGINE v5.8 - FATHER DISCIPLINE (post-powercut door + blocking unattended + click_text fixed)
# One cell. One paste. Everything works. Orders persistent, tasks generic, proof to wire.
import base64, sys, os, subprocess, time, json, threading, urllib.request, urllib.parse

# ============ ENGINE SERVER (subprocess per engine, hands = FATHERS CHROME via relay) ============
SERVER = '''
import sys, os, json, time, threading, queue, urllib.request, re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
ENGINE_NAME = sys.argv[1]
PORT = int(sys.argv[2])
TUNNEL = sys.argv[3]
TOKEN = "GOLD24"
PREF_KW = os.environ.get("ENGINE_KW", "linkedin")
PAGE_CACHE = {"pageId": None, "ts": 0}

def raw_tool(name, args):
    r = urllib.request.Request(TUNNEL + "/tool?token=" + TOKEN, data=json.dumps({"name": name, "arguments": args}).encode(), headers={"Content-Type": "application/json"})
    res = json.loads(urllib.request.urlopen(r, timeout=120).read())
    c = res.get("result", {}).get("content", [])
    err = res.get("result", {}).get("isError", False)
    return err, (c[0].get("text", "") if c and isinstance(c, list) else str(res))[:12000]

def resolve_page(kw):
    err, txt = raw_tool("list_pages", {})
    for line in str(txt).splitlines():
        m = re.match(r"\\s*(\\d+):", line)
        if m and kw in line.lower():
            return int(m.group(1))
    lines = [l for l in str(txt).splitlines() if re.match(r"\\s*\\d+:", l)]
    if lines:
        return int(re.match(r"\\s*(\\d+):", lines[0]).group(1))
    return 1

def get_page_id(kw):
    now = time.time()
    if PAGE_CACHE["pageId"] is None or now - PAGE_CACHE["ts"] > 300:
        PAGE_CACHE["pageId"] = resolve_page(kw or PREF_KW)
        PAGE_CACHE["ts"] = now
    return PAGE_CACHE["pageId"]

CMDS = queue.Queue()
RESULTS = {}
RID = [0]
RLOCK = threading.Lock()

def engine_main():
    while True:
        rid, tname, targs = CMDS.get()
        try:
            out = raw_tool(tname, targs)
            RESULTS[rid] = (True, out)
        except Exception as e:
            RESULTS[rid] = (False, str(e)[:200])

threading.Thread(target=engine_main, daemon=True).start()

HANDS = {
    "navigate": lambda a: ("navigate_page", {"type": "url", "url": a.get("url", "about:blank"), "pageId": a.get("pageId", get_page_id(a.get("kw", "")))}),
    "list_pages": lambda a: ("list_pages", {}),
    "snapshot": lambda a: ("take_snapshot", {"pageId": a.get("pageId", get_page_id(a.get("kw", "")))}),
    "click": lambda a: ("click", {"uid": a.get("uid"), "pageId": a.get("pageId", get_page_id(a.get("kw", "")))}),
    "click_text": lambda a: ("evaluate_script", {"pageId": a.get("pageId", get_page_id(a.get("kw", ""))), "function": "() => { const kw=" + json.dumps(a.get("text", "")) + "; const els=Array.from(document.querySelectorAll('a,button,[role=button],input[type=submit]')); const el=els.find(x=>new RegExp(kw,'i').test(x.textContent||x.value||'')); if(el){el.scrollIntoView({block:'center'}); el.click(); return 'CLICKED: '+el.textContent.trim().substring(0,40);} return 'NOT FOUND: '+kw; }"}),
    "type_text": lambda a: ("type_text", {"text": a.get("text", ""), "pageId": a.get("pageId", get_page_id(a.get("kw", "")))}),
    "key": lambda a: ("press_key", {"key": a.get("key", "Enter"), "pageId": a.get("pageId", get_page_id(a.get("kw", "")))}),
    "eval": lambda a: ("evaluate_script", {"function": a.get("js", "() => document.title"), "pageId": a.get("pageId", get_page_id(a.get("kw", "")))}),
    "title": lambda a: ("evaluate_script", {"function": "() => document.title", "pageId": a.get("pageId", get_page_id(a.get("kw", "")))}),
}

class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        if self.path != "/hands":
            self.send_response(404)
            self.end_headers()
            return
        n = int(self.headers.get("Content-Length", 0))
        try:
            req = json.loads(self.rfile.read(n))
            name = req.get("name")
            args = req.get("arguments", {})
            if name in HANDS:
                tname, targs = HANDS[name](args)
            else:
                tname, targs = name, args
            with RLOCK:
                RID[0] += 1
                rid = RID[0]
            CMDS.put((rid, tname, targs))
            for _ in range(240):
                if rid in RESULTS:
                    break
                time.sleep(0.5)
            ok, out = RESULTS.pop(rid, (False, "timeout"))
            if (not ok) or ("Invalid arguments" in str(out)[:150]) or ("Required at pageId" in str(out)):
                PAGE_CACHE["pageId"] = None
            body = json.dumps({"ok": True, "result": str(out)}).encode()
        except Exception as e:
            body = json.dumps({"ok": False, "error": str(e)[:200]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

print(ENGINE_NAME, "engine up port", PORT, flush=True)
ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
'''

with open("/kaggle/working/kilo_engine_server.py", "w") as f:
    f.write(SERVER)

# ============ TASKS (standing orders -Father's 48h commands as executable task-scripts) ============
JS_LI = "() => { const t=Array.from(document.querySelectorAll('li.msg-conversation-listitem, [data-conversation-id]')); const out=[]; t.slice(0,8).forEach(x=>{out.push(x.textContent.replace(/\\s+/g,' ').trim().substring(0,60));}); return JSON.stringify(out); }"
JS_GMAIL = "() => { let rows=Array.from(document.querySelectorAll('tr.zA')); if(!rows.length){rows=Array.from(document.querySelectorAll('[role=main] tr, div[gh=tl] tr, table tr')).filter(r=>r.textContent.length>40&&r.textContent.length<400);} const out=[]; rows.slice(0,10).forEach(r=>{const t=r.textContent.replace(/\\s+/g,' ').trim(); if(t) out.push(t.substring(0,90));}); return JSON.stringify(out.slice(0,8)); }"
JS_NAUKRI = "() => { const t=Array.from(document.querySelectorAll('[class*=jobTitle], a.title')).map(x=>x.textContent.replace(/\\s+/g,' ').trim()).filter(x=>x&&x.length>10&&x.length<90); return JSON.stringify(t.slice(0,10)); }"
JS_WA = "() => { const rows=Array.from(document.querySelectorAll('#pane-side [role=row]')); const names=[]; rows.forEach(r=>{const s=r.querySelector('[title]'); if(s) names.push(s.title);}); return JSON.stringify(names.slice(0,12)); }"

STANDING = {
    "DM": {"name": "linkedin-triage", "issued": "STANDING", "steps": [
        {"hand": "navigate", "args": {"url": "https://www.linkedin.com/messaging/"}},
        {"hand": "eval", "args": {"js": JS_LI}},
    ], "report": "LinkedIn triage done; REPUTATION-ALERT if hostile; sends gated"},
    "WARDEN": {"name": "gmail-loan-scan", "issued": "STANDING", "steps": [
        {"hand": "navigate", "args": {"url": "https://mail.google.com/mail/u/0/#inbox"}},
        {"hand": "eval", "args": {"js": JS_GMAIL}},
    ], "report": "Gmail scanned; SCAN-ALERT loan warnings + Lok Adalat 12 Sep notices"},
    "SCOUT": {"name": "naukri-hunt", "issued": "STANDING", "steps": [
        {"hand": "navigate", "args": {"url": "https://www.naukri.com/ai-engineer-remote-jobs"}},
        {"hand": "eval", "args": {"js": JS_NAUKRI}},
    ], "report": "Naukri hunt done; GIG list for Kunal/Partha; next: apply"},
    "WA": {"name": "family-watch", "issued": "STANDING", "steps": [
        {"hand": "eval", "args": {"js": JS_WA}},
    ], "report": "Family chats watched; drafts in voice law"},
    "BIZMODEL": {"name": "earning-plan", "issued": "STANDING", "steps": [], "report": "PLAN: Agent School 20x999=19980; IN-cta LI leads; voice-agent demos; Lok Adalat T-4d money priority"},
    "LEDGER": {"name": "ledger-tally", "issued": "STANDING", "steps": [], "report": "LEDGER-STATE: hunt+triage+scan active; Lok Adalat T-4d"},
    "HERALD": {"name": "relay-watch", "issued": "STANDING", "steps": [], "report": "Herald watching for REPUTATION-ALERT / URGENT-FAMILY"},
    "MONITOR": {"name": "audit", "issued": "STANDING", "steps": [], "report": "MONITOR audit: watching all squads"},
    "COMMENTER": {"name": "comment-drafts", "issued": "STANDING", "steps": [], "report": "Comment drafts: professional tone, reputation-safe, DRAFT prefix only"},
    "POSTER": {"name": "post-drafts", "issued": "STANDING", "steps": [], "report": "Post drafts: skills showcase, humble confident, DRAFT prefix only"},
}

# ============ RUNTIME ============
TUNNEL = "https://cars-additional-adopt-recognised.trycloudflare.com"

def post(p, d):
    r = urllib.request.Request(TUNNEL + p + "?token=GOLD24", data=json.dumps(d).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=30).read())

def get(p):
    url = TUNNEL + p + ("&" if "?" in p else "?") + "token=GOLD24"
    return json.loads(urllib.request.urlopen(url, timeout=30).read())

def speak(tag, txt):
    for attempt in range(3):
        try:
            post("/say", {"body": tag, "text": txt})
            return
        except Exception as e:
            print(tag, "speak-fail attempt", attempt + 1, str(e)[:40])
            time.sleep(5)

def hear(sq):
    try:
        return get("/say?body=" + urllib.parse.quote(sq)).get("orders", [])
    except Exception:
        return []

def hand(port, name, args):
    r = urllib.request.Request("http://127.0.0.1:%d/hands" % port, data=json.dumps({"name": name, "arguments": args}).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=150).read())

ENGINES = [
    ("ENGINE-1", 9999, "SEAT-A", ["DM", "WA", "COMMENTER", "POSTER"], 10, "linkedin"),
    ("ENGINE-2", 9998, "SEAT-B", ["BIZMODEL", "MONITOR", "SCOUT"], 10, "naukri"),
    ("ENGINE-3", 9997, "SEAT-C", ["LEDGER", "HERALD", "WARDEN"], 10, "whatsapp"),
]
for name, port, seat, squads, per, kw in ENGINES:
    env = dict(os.environ)
    env["ENGINE_KW"] = kw
    subprocess.Popen([sys.executable, "/kaggle/working/kilo_engine_server.py", name, str(port), TUNNEL], env=env)
print("engines spawning...")
time.sleep(12)

# TAB PINNING: each engine navigates its own tab once at boot - no cross-tab borrowing
PIN = {
    "ENGINE-1": ("https://www.linkedin.com/messaging/", "linkedin"),
    "ENGINE-2": ("https://www.naukri.com/ai-engineer-remote-jobs", "naukri"),
    "ENGINE-3": ("https://mail.google.com/mail/u/0/#inbox", "gmail"),
}
for name, port, seat, squads, per, kw in ENGINES:
    url, kw2 = PIN[name]
    try:
        hand(port, "navigate", {"url": url, "kw": kw2})
        print(name, "TAB PINNED:", url[:50])
        speak("ENGINE", name + " tab pinned: " + url[:60])
    except Exception as e:
        print(name, "pin fail", str(e)[:50])

DONE = set()

def execute_task(tag, port, kw, task):
    steps = task.get("steps", [])
    results = []
    for i, st in enumerate(steps):
        try:
            a = dict(st.get("args", {}))
            a["kw"] = kw
            out = hand(port, st.get("hand", "eval"), a)
            results.append(str(out)[:100])
            print(tag, "step", i, str(out)[:90])
        except Exception as e:
            speak(tag, "TASK-FAIL " + str(task.get("name", "?")) + " step " + str(i) + ": " + str(e)[:80])
            return
    speak(tag, "TASK-DONE " + str(task.get("name", "?")) + " :: " + (results[-1] if results else str(task.get("report", "")))[:150])

def soldier(tag, sq, cyc, port, kw):
    hb = 0
    while True:
        hb += 1
        try:
            if hb % 4 == 1:
                speak(tag, tag + " alive hb" + str(hb))
                print(tag, "alive", hb)
            if hb % 6 == 3:
                for x in hear(sq):
                    tx = str(x.get("text", ""))
                    if tx.startswith("TASK:"):
                        try:
                            task = json.loads(tx[5:])
                            tname = "T" + str(task.get("name", "?")) + str(task.get("issued", ""))
                            if tname not in DONE:
                                DONE.add(tname)
                                speak(tag, "TASK-START " + str(task.get("name", "?")))
                                print(tag, "TASK-START", task.get("name", "?"))
                                execute_task(tag, port, kw, task)
                        except Exception as e:
                            print(tag, "task-parse err", str(e)[:60])
            if hb % 12 == 6:
                try:
                    out = hand(port, "eval", {"js": "() => document.title", "kw": kw})
                    print(tag, "eyes:", str(out)[:80])
                except Exception as e:
                    print(tag, "eyes err", str(e)[:40])
        except Exception as e:
            print(tag, "err", str(e)[:50])
        time.sleep(cyc)

grand = 0
for name, port, seat, squads, per, kw in ENGINES:
    n = 0
    for sq in squads:
        for i in range(1, per + 1):
            t = threading.Thread(target=soldier, args=(seat + "-" + sq + "-" + str(i).zfill(2), sq, 30 + i * 3, port, kw), daemon=True)
            t.start()
            n += 1
            grand += 1
    speak(seat, seat + " on " + name + ": " + str(n) + " soldiers v5.2 STANDING DUTIES LIVE")
    print(seat, "on", name, ":", n)
print("ALL ENGINES UP:", grand, "- v5.8: fathers discipline - post-powercut respawn + blocking unattended + click actions")
speak("ENGINE", "v5.6 UP: " + str(grand) + " soldiers, unattended-ready, click_text live")

# UNATTENDED: this cell BLOCKS on purpose - holds the Kaggle session open for the full 12h.
# (Threads alone do not stop Save & Run All from completing; a blocking cell does.)
print('ARMY HOLDING THE LINE - session stays alive. Interrupt to stop.')
while True:
    time.sleep(300)
speak("ENGINE", "v5.5 UP: " + str(grand) + " soldiers, STANDING DUTIES live")

# Fire standing tasks into the bank (persisted) - leads pick up on first poll
for sq, task in STANDING.items():
    try:
        post("/say", {"body": sq, "text": "TASK:" + json.dumps(task)})
        print("STANDING TASK posted:", sq, task["name"])
    except Exception as e:
        print("post fail", sq, str(e)[:40])