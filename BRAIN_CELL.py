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

def wa_send_compound(chat_name, message):
    """Screen-verified WhatsApp send (2026-09-09 method): resolve WA pageId -> snapshot -> real CDP click on
    chat row -> click composer -> type_text with Enter -> verify preview text."""
    import re as _re
    try:
        pid = resolve_page("whatsapp")
        # v6.3.4: NEVER reload a live WA tab - reload wipes the chat list for 15-30s.
        # Snapshot the live tab first; navigate only if the chat list is not ready.
        r = None
        m = None
        for _w in range(10):
            r = tool("take_snapshot", {"pageId": pid})
            txt = json.dumps(r)
            m = _re.search(r'uid=(\S+) gridcell \\"?' + _re.escape(chat_name), txt)
            if m:
                break
            if _w == 0:
                tool("navigate_page", {"type": "url", "url": "https://web.whatsapp.com/", "pageId": pid})
            time.sleep(3)
        if not m:
            return {"wa": "NO ROW " + chat_name + " (list not ready)"}
        tool("click", {"uid": m.group(1), "pageId": pid})
        time.sleep(3)
        r = tool("take_snapshot", {"pageId": pid})
        txt = json.dumps(r)
        m2 = _re.search(r'uid=(\S+) textbox \\"?Type a message to ' + _re.escape(chat_name), txt)
        if not m2:
            return {"wa": "NO COMPOSER " + chat_name}
        tool("click", {"uid": m2.group(1), "pageId": pid})
        time.sleep(1)
        tool("type_text", {"pageId": pid, "text": message, "submitKey": "Enter"})
        time.sleep(4)
        r = tool("take_snapshot", {"pageId": pid})
        ok = message[:25] in json.dumps(r)
        return {"wa": "SENT+VERIFIED" if ok else "SENT-UNVERIFIED", "chat": chat_name}
    except Exception as e:
        return {"wa": "FAIL", "err": str(e)[:100]}

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
            elif hand == "adb":
                out = tool("adb", {"args": a.get("args", [])})
            elif hand == "wa_send":
                out = wa_send_compound(a.get("chat", ""), a.get("message", ""))
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
    say("KILO", tag + " v6.3-free ON DUTY. squads [" + ",".join(conf["squads"]) + "] internal x10. boot cutoff " + BOOT_AT + " poll 5m")
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
            if hb % 6 == 1:
                say("KILO", tag + " alive hb" + str(hb) + " v6.3-free 5m poll boot-cutoff " + BOOT_AT)
            if hb % 3 == 2:
                save_state()
        except Exception as e:
            print(tag, "loop err", str(e)[:60], flush=True)
        time.sleep(300)

def internal_soldier(seat, sq, idx):
    tag = seat + "-" + sq + "-" + str(idx).zfill(2)
    while True:
        time.sleep(120 + idx * 7)

def metrics_loop():
    """Unattended vitals: Kaggle CPU/RAM/load -> wire every 10 min. Father watches via Kilo, never via UI."""
    import subprocess
    ncpu = os.cpu_count() or 2
    prev = None
    while True:
        try:
            cpu = None
            try:
                with open("/proc/stat") as f:
                    parts = f.readline().split()[1:]
                vals = [int(x) for x in parts[:8]]
                idle = vals[3] + vals[4]
                total = sum(vals)
                if prev is not None:
                    d_idle = idle - prev[0]
                    d_total = total - prev[1]
                    if d_total > 0:
                        cpu = round(100 * (1 - d_idle / d_total), 1)
                prev = (idle, total)
            except Exception:
                pass
            load1, load5, load15 = [round(x, 2) for x in os.getloadavg()]
            mem = {}
            try:
                with open("/proc/meminfo") as f:
                    for line in f:
                        k, v = line.split(":")
                        mem[k.strip()] = int(v.strip().split()[0])
                ram_used = mem["MemTotal"] - mem["MemAvailable"]
                ram_pct = round(100 * ram_used / mem["MemTotal"], 1)
                ram_gb = round(ram_used / 1048576, 2)
            except Exception:
                ram_pct = ram_gb = -1
            nthr = threading.active_count()
            say("KILO", "KAGGLE-METRICS cpu=" + (str(cpu) + "%" if cpu is not None else "warming") +
                " ram=" + str(ram_pct) + "% (" + str(ram_gb) + "GB) load=" + str(load5) +
                " cores=" + str(ncpu) + " threads=" + str(nthr) + " tasks_done=" + str(len(done_names)))
        except Exception as e:
            print("metrics err", str(e)[:60], flush=True)
        time.sleep(600)

def main():
    print("KILO BRAIN v6.3 BOOT - boot cutoff: " + BOOT_AT, flush=True)
    print("hands: browser + adb(phone) + wa_send compound. Ownership law: long-horizon, self-check, 24/7.", flush=True)
    for seat, conf in SEATS.items():
        threading.Thread(target=lead_loop, args=(seat, conf), daemon=True).start()
        for sq in conf["squads"]:
            for i in range(2, 11):
                threading.Thread(target=internal_soldier, args=(seat, sq, i), daemon=True).start()
    threading.Thread(target=metrics_loop, daemon=True).start()
    print("BRAIN UP: 3 leads, adb+wa_send hands, metrics live", flush=True)
    say("KILO", "BRAIN v6.3 LIVE: adb phone hand + wa_send compound + boot cutoff " + BOOT_AT + ". Army owns outcomes, 24/7.")
    while True:
        time.sleep(300)
        save_state()

main()
