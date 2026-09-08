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
        m = re.match(r"\s*(\d+):", line)
        if m and kw in line.lower():
            return int(m.group(1))
    lines = [l for l in str(txt).splitlines() if re.match(r"\s*\d+:", l)]
    if lines:
        return int(re.match(r"\s*(\d+):", lines[0]).group(1))
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

print(ENGINE_NAME, "hands-proxy up port", PORT, "-> FATHERS CHROME via relay", flush=True)
ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
