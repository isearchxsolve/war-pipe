# KILO BRAIN v6.1 - PAGE RESOLVER + BOOT CUTOFF (fix: -32602 raw-MCP calls + backlog storm)
# One cell. stdlib only. Door baked (PERMANENT ngrok static domain).
# laptop = hands + gate + vault ONLY. Kaggle = queue + scheduler + leads + drafting.
# LEAD FUNNEL: only 3 leads touch the wire. v6.1: leads resolve pageId per kw (cache 300s),
# boot cutoff - tasks posted BEFORE brain boot are marked seen, never executed.
import sys, os, time, json, threading, urllib.request, urllib.parse, re
from datetime import datetime, timezone

T = "https://meredith-impermissible-unsportively.ngrok-free.dev"
TOK = "GOLD24"
STATE_FILE = "/kaggle/working/brain_state.json"
BOOT_AT = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

SEATS = {
    "SEAT-A": {"squads": ["DM", "WA", "COMMENTER", "POSTER"], "kw": "linkedin"},
    "SEAT-B": {"squads": ["BIZMODEL", "MONITOR", "SCOUT"], "kw": "naukri"},
    "SEAT-C": {"squads": ["LEDGER", "HERALD", "WARDEN"], "kw": "whatsapp"},
}

done_names = set()
try:
    with open(STATE_FILE) as f:
        done_names = set(json.load(f).get("done", []))
except Exception:
    pass
state_lock = threading.Lock()
page_cache = {}   # kw -> (pageId, ts)

def save_state():
    try:
        with state_lock:
            with open(STATE_FILE, "w") as f:
                json.dump({"done": sorted(done_names)[-500:], "boot": BOOT_AT}, f)
    except Exception:
        pass

def say(body, text, retries=3):
    for i in range(retries):
        try:
            b = json.dumps({"body": body, "text": text}).encode()
            req = urllib.request.Request(T + "/say?token=" + TOK, data=b, method="POST",
                                         headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=20)
            return True
        except Exception:
            time.sleep(3 * (i + 1))
    return False

def tool(name, args, timeout=150):
    b = json.dumps({"name": name, "arguments": args}).encode()
    req = urllib.request.Request(T + "/tool?token=" + TOK, data=b, method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

def resolve_page(kw):
    c = page_cache.get(kw)
    if c and time.time() - c[1] < 300:
        return c[0]
    txt = str(tool("list_pages", {}))
    pid = None
    for line in txt.splitlines():
        m = re.match(r"\s*(\d+):", line)
        if m and kw.lower() in line.lower():
            pid = int(m.group(1)); break
    if pid is None:
        m = re.search(r"\s*(\d+):", txt)
        pid = int(m.group(1)) if m else 1
    page_cache[kw] = (pid, time.time())
    return pid

def call(name, args, kw):
    """MCP call with pageId resolution + one invalidation retry."""
    for attempt in (1, 2):
        a2 = dict(args)
        a2["pageId"] = resolve_page(kw)
        out = tool(name, a2)
        s = str(out)
        if ("-32602" in s) or ("Invalid arguments" in s) or ("Required at pageId" in s):
            page_cache.pop(kw, None)
            if attempt == 2:
                return out
            time.sleep(2)
            continue
        return out
    return {"error": "unresolved"}

def hear_orders(names):
    polled = []
    for nm in names:
        try:
            u = T + "/say?body=" + urllib.parse.quote(nm) + "&token=" + TOK
            with urllib.request.urlopen(u, timeout=25) as r:
                polled.extend(json.loads(r.read().decode()).get("orders", []))
        except Exception:
            pass
    return polled

def execute_steps(lead_tag, seat, task):
    name = task.get("name", "?")
    kw = SEATS[seat]["kw"]
    results = []
    ok_all = True
    for i, st in enumerate(task.get("steps", [])[:12]):
        hand = st.get("hand")
        a = dict(st.get("args", {}))
        try:
            if hand == "eval":
                out = call("evaluate_script", {"function": a.get("js", "() => document.title")}, a.get("kw", kw))
            elif hand == "navigate":
                out = call("navigate_page", {"type": "url", "url": a.get("url", "about:blank")}, a.get("kw", kw))
            elif hand == "key":
                out = call("press_key", {"key": a.get("key", "Enter")}, a.get("kw", kw))
            elif hand == "list_pages":
                out = tool("list_pages", {})
            elif hand == "title":
                out = call("evaluate_script", {"function": "() => document.title"}, a.get("kw", kw))
            elif hand == "snapshot":
                out = call("take_snapshot", {}, a.get("kw", kw))
            else:
                out = {"skipped": hand}
        except Exception as e:
            ok_all = False
            say("KILO", lead_tag + " TASK-FAIL " + name + " step " + str(i) + ": " + str(e)[:100])
            break
        s = str(out)[:160]
        results.append(s)
        print(lead_tag, "step", i, s[:90], flush=True)
        if ("isError" in s) or ("Invalid arguments" in s):
            ok_all = False
            break
        time.sleep(2)
    receipt = str(task.get("report", ""))[:100] + " | last: " + (results[-1][:130] if results else "none")
    kind = "TASK-DONE" if (ok_all and task.get("steps")) else "TASK-FAIL"
    say("KILO", lead_tag + " " + kind + " " + name + " :: " + receipt)

def lead_loop(seat, conf):
    tag = seat + "-LEAD"
    say("KILO", tag + " v6.1 ON DUTY. squads [" + ",".join(conf["squads"]) + "] internal x10. boot cutoff " + BOOT_AT)
    hb = 0
    while True:
        hb += 1
        try:
            polled = hear_orders([seat] + conf["squads"])
            for o in polled:
                tx = str(o.get("text", ""))
                at = str(o.get("at", ""))[:19]
                if not tx.startswith("TASK:"):
                    continue
                if at < BOOT_AT:   # boot cutoff - history is seen, never executed
                    continue
                try:
                    task = json.loads(tx[5:])
                except Exception:
                    continue
                key = str(task.get("name", "?")) + "|" + str(task.get("issued", ""))
                with state_lock:
                    if key in done_names:
                        continue
                    done_names.add(key)
                say("KILO", tag + " TASK-START " + str(task.get("name", "?")))
                threading.Thread(target=execute_steps, args=(tag, seat, task), daemon=True).start()
            if hb % 10 == 1:
                say("KILO", tag + " alive hb" + str(hb) + " v6.1 boot-cutoff " + BOOT_AT)
            if hb % 5 == 2:
                save_state()
        except Exception as e:
            print(tag, "loop err", str(e)[:60], flush=True)
        time.sleep(60)

def internal_soldier(seat, sq, idx):
    tag = seat + "-" + sq + "-" + str(idx).zfill(2)
    while True:
        time.sleep(120 + idx * 7)

def main():
    print("KILO BRAIN v6.1 BOOT - boot cutoff: " + BOOT_AT, flush=True)
    print("architecture: laptop=hands+gate+vault | kaggle=queue+leads. History marked seen.", flush=True)
    for seat, conf in SEATS.items():
        threading.Thread(target=lead_loop, args=(seat, conf), daemon=True).start()
        for sq in conf["squads"]:
            for i in range(2, 11):
                threading.Thread(target=internal_soldier, args=(seat, sq, i), daemon=True).start()
    print("BRAIN UP: 3 leads on wire, 27 internal, history filtered", flush=True)
    say("KILO", "BRAIN v6.1 LIVE: pageId resolver + boot cutoff " + BOOT_AT + ". Old backlog marked seen.")
    while True:
        time.sleep(300)
        save_state()

main()
