import base64, ast, io, textwrap

SERVER = textwrap.dedent("""
import sys, os, json, time, threading, queue, urllib.request, re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ENGINE_NAME = sys.argv[1] if len(sys.argv) > 1 else "ENGINE-1"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 9999
TUNNEL = sys.argv[3] if len(sys.argv) > 3 else ""
TOKEN = "GOLD24"
PREF_KW = os.environ.get("ENGINE_KW", "linkedin")
PAGE_CACHE = {"pageId": None}

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
        m = re.match(r"\\s*(\\d+):", lines[0])
        return int(m.group(1))
    return 1

def get_page_id(kw):
    if PAGE_CACHE["pageId"] is None:
        PAGE_CACHE["pageId"] = resolve_page(kw or PREF_KW)
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

HAND_ALIASES = {
    "navigate": ("navigate_page", lambda a: {"type": "url", "url": a.get("url", "about:blank"), "pageId": a.get("pageId", get_page_id(a.get("kw", "")))}),
    "list_pages": ("list_pages", lambda a: {}),
    "snapshot": ("take_snapshot", lambda a: {"pageId": a.get("pageId", get_page_id(a.get("kw", "")))}),
    "click": ("click", lambda a: {"uid": a.get("uid"), "pageId": a.get("pageId", get_page_id(a.get("kw", "")))}),
    "type_text": ("type_text", lambda a: {"text": a.get("text", ""), "pageId": a.get("pageId", get_page_id(a.get("kw", "")))}),
    "key": ("press_key", lambda a: {"key": a.get("key", "Enter"), "pageId": a.get("pageId", get_page_id(a.get("kw", "")))}),
    "eval": ("evaluate_script", lambda a: {"function": a.get("js", a.get("function", "() => document.title")), "pageId": a.get("pageId", get_page_id(a.get("kw", "")))}),
    "title": ("evaluate_script", lambda a: {"function": "() => document.title", "pageId": a.get("pageId", get_page_id(a.get("kw", "")))}),
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
            if name in HAND_ALIASES:
                tname, argf = HAND_ALIASES[name]
                targs = {k: v for k, v in argf(args).items() if v is not None}
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
            if (not ok) or ("isError" in str(out)[:80]) or ("Invalid arguments" in str(out)[:150]) or ("Required at pageId" in str(out)):
                PAGE_CACHE["pageId"] = None
                try:
                    PAGE_CACHE["pageId"] = resolve_page(args.get("kw", PREF_KW))
                except Exception:
                    pass
            body = json.dumps({"ok": True, "result": str(out)}).encode()
        except Exception as e:
            body = json.dumps({"ok": False, "error": str(e)[:200]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

print(ENGINE_NAME, "hands-proxy up on port", PORT, "-> FATHERS CHROME via relay, kw=" + PREF_KW, flush=True)
ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
""").lstrip()

CELL = textwrap.dedent("""
# KILO ENGINES v4.1 PERMANENT - multiple engines per Kaggle instance, hands = FATHERS CHROME via relay
import base64, sys, os, subprocess, time, json, threading, urllib.request, urllib.parse
ENGINE_SRC = base64.b64decode("ENG_B64").decode()
with open("/kaggle/working/kilo_engine_server.py", "w") as f:
    f.write(ENGINE_SRC)
TUNNEL = "https://delivering-syndicate-musician-charge.trycloudflare.com"

def post(p, d):
    r = urllib.request.Request(TUNNEL + p + "?token=GOLD24", data=json.dumps(d).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=30).read())

def get(p):
    return json.loads(urllib.request.urlopen(TUNNEL + p + "?token=GOLD24", timeout=30).read())

def speak(tag, txt):
    try:
        post("/say", {"body": tag, "text": txt})
    except Exception as e:
        print(tag, "speak-fail", str(e)[:40])

def hear(sq):
    try:
        return get("/hear?body=" + urllib.parse.quote(sq)).get("reports", [])
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
PROCS = {}
for name, port, seat, squads, per, kw in ENGINES:
    env = dict(os.environ)
    env["ENGINE_KW"] = kw
    p = subprocess.Popen([sys.executable, "/kaggle/working/kilo_engine_server.py", name, str(port), TUNNEL], env=env)
    PROCS[name] = p
    print(name, "spawned pid", p.pid, "port", port, "kw", kw)
print("waiting for engines...")
time.sleep(12)
for name, port, seat, squads, per, kw in ENGINES:
    p = PROCS[name]
    if p.poll() is not None:
        print(name, "DIED rc", p.returncode)
        speak("ENGINE", name + " DIED " + str(p.returncode))
    else:
        print(name, "ALIVE hands-proxy -> fathers chrome")

def soldier(tag, sq, cyc, port, kw, duties):
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
                    if "DUTY:" in tx:
                        print(tag, "ORDERS:", tx[:80])
            if hb % 6 == 1:
                for dname, dfn in duties.items():
                    try:
                        out = dfn()
                        if out:
                            print(tag, dname, str(out)[:100])
                            speak(tag, tag + " " + dname + " " + str(out)[:150])
                    except Exception as e:
                        print(tag, dname, "err", str(e)[:60])
        except Exception as e:
            print(tag, "err", str(e)[:50])
        time.sleep(cyc)

grand = 0
for name, port, seat, squads, per, kw in ENGINES:
    duties_for = {
        "SCOUT": {"hunt": lambda: hand(port, "eval", {"js": "() => document.title + ' | ' + location.href", "kw": "naukri"})},
        "DM": {"triage": lambda: hand(port, "eval", {"js": "() => document.title + ' | ' + location.href", "kw": "linkedin"})},
        "WARDEN": {"scan": lambda: hand(port, "title", {"kw": "whatsapp"})},
    }
    n = 0
    for sq in squads:
        d = duties_for.get(sq, {"watch": lambda: hand(port, "title", {"kw": kw})})
        for i in range(1, per + 1):
            t = threading.Thread(target=soldier, args=(seat + "-" + sq + "-" + str(i).zfill(2), sq, 30 + i * 3, port, kw, d), daemon=True)
            t.start()
            n += 1
            grand += 1
    speak(seat, seat + " on " + name + ": " + str(n) + " soldiers, hands = FATHERS CHROME")
    print(seat, "on", name, ":", n, "soldiers")
print("ALL ENGINES UP:", grand, "SOLDIERS TOTAL - fathers chrome is the only browser")
speak("ENGINE", "ALL UP: " + str(grand) + " soldiers, hands=fathers chrome")
""").lstrip()

ast.parse(SERVER)
print('SERVER SYNTAX CLEAN')
ast.parse(CELL)
print('CELL SYNTAX CLEAN')
b64 = base64.b64encode(SERVER.encode()).decode()
CELL = CELL.replace('ENG_B64', b64)
ast.parse(CELL)
print('CELL EMBEDDED CLEAN')
with io.open(r'D:\anonym\war-pipe\kilo-core\engine_server.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(SERVER)
with io.open(r'D:\anonym\war-pipe\kilo-core\engine_cell.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(CELL)
print('PERMANENT FILES WRITTEN: D:\\anonym\\war-pipe\\kilo-core\\engine_server.py + engine_cell.py')
