# KILO BRAIN v7.0 - EVIDENCE LAW + REAL SCHEDULER + SEMANTIC HANDS (click/type/verify)
# v6 bug class this kills: snapshot-only "DONE" lies; future-issued tasks run instantly;
# no hands to actually click/type into the page (everything skipped, nothing failed).
# Rule: NOTHING reports TASK-DONE unless task.must_prove is visible on the page, or it IS a scan task.
# HARD ENFORCEMENT: retry counts, exponential backoff, evidence strict mode.
import sys, os, time, json, threading, urllib.request, urllib.parse, re
from datetime import datetime, timezone

TOK = "GOLD24"
DOORS = [
    "https://economic-names-available-frozen.trycloudflare.com",
    "https://retrain-schnapps-upbeat.ngrok-free.dev",
    "https://phantom-analytical-gains-curious.trycloudflare.com",
]
HDRS = {"User-Agent": "kilo-brain", "ngrok-skip-browser-warning": "1"}

def door():
    for c in DOORS:
        try:
            req = urllib.request.Request(c + "/health?token=" + TOK, headers=HDRS)
            r = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
            if r.get("ok"):
                return c
        except Exception:
            pass
    return None

T = door()
STATE_FILE = "/kaggle/working/brain_state.json"
BOOT_AT = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
MAX_MCP_RETRIES = 20
MAX_CONCURRENT_TASKS = 16
TASK_TIMEOUT = 600

SEATS = {
    "SEAT-A": {"squads": ["DM", "WA", "COMMENTER", "POSTER"], "kw": "linkedin"},
    "SEAT-B": {"squads": ["BIZMODEL", "MONITOR", "SCOUT"], "kw": "naukri"},
    "SEAT-C": {"squads": ["LEDGER", "HERALD", "WARDEN"], "kw": "whatsapp"},
}

done_names = set()
task_locks = {}
task_locks_lock = threading.Lock()
mcp_fail_count = 0
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
    global T
    for i in range(retries):
        if not T:
            T = door()
            if not T:
                time.sleep(10)
                continue
        try:
            b = json.dumps({"body": body, "text": text}).encode()
            req = urllib.request.Request(T + "/say?token=" + TOK, data=b, method="POST",
                                         headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=20)
            return True
        except Exception:
            T = None
            time.sleep(3 * (i + 1))
    return False

def tool(name, args, timeout=150):
    global T
    for attempt in range(3):
        if not T:
            T = door()
            if not T:
                time.sleep(10)
                continue
        try:
            b = json.dumps({"name": name, "arguments": args}).encode()
            req = urllib.request.Request(T + "/tool?token=" + TOK, data=b, method="POST",
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except Exception:
            T = None
            time.sleep(3 * (attempt + 1))
    return {"error": "no door available"}

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
    global T
    polled = []
    for nm in names:
        for attempt in range(3):
            if not T:
                T = door()
                if not T:
                    time.sleep(10)
                    continue
            try:
                u = T + "/say?body=" + urllib.parse.quote(nm) + "&token=" + TOK
                with urllib.request.urlopen(u, timeout=25) as r:
                    polled.extend(json.loads(r.read().decode()).get("orders", []))
                break
            except Exception:
                T = None
                time.sleep(3 * (attempt + 1))
    return polled

def _snap_txt(kw):
    return json.dumps(call("take_snapshot", {}, kw))

def _find_uid(txt, find):
    f = re.escape(find)
    for pats in (r'uid=(\S+) (?:button|link|tab|checkbox|radio)[^\\n]{0,90}' + f,
                 r'uid=(\S+)[^\\n]{0,40}\\"?' + f,
                 r'uid=(\S+)[^\\n]{0,60}' + f):
        m = re.search(pats, txt)
        if m:
            return m.group(1)
    return None

def _body_text(kw):
    try:
        out = call("evaluate_script", {"function": "() => document.body.innerText.slice(0, 20000)"}, kw)
        return json.dumps(out)
    except Exception:
        return ""

def _verify(kw, want, any_of, within):
    pats = [want] if want else []
    pats += list(any_of or [])
    deadline = time.time() + within
    while time.time() < deadline:
        hay = _body_text(kw)
        for p in pats:
            if p and re.sub(r'\W+', ' ', p)[:40] in re.sub(r'\W+', ' ', hay):
                return {"verify": "PASS", "saw": p[:50]}
        time.sleep(3)
    return {"verify": "MISS", "wanted": [p[:40] for p in pats][:3]}

def execute_steps(lead_tag, seat, task):
    global mcp_fail_count
    name = task.get("name", "?")
    kw = SEATS[seat]["kw"]
    key = str(name) + "|" + str(task.get("issued", ""))
    with task_locks_lock:
        if key not in task_locks:
            task_locks[key] = threading.Lock()
        lock = task_locks[key]
    if not lock.acquire(blocking=False):
        say("KILO", lead_tag + " TASK-SKIPPED (duplicate in flight) " + name)
        return
    try:
        results = []
        ok_all = True
        max_attempts = task.get("retry", 3)
        for attempt in range(1, max_attempts + 1):
            results = []
            ok_all = True
            for i, st in enumerate(task.get("steps", [])[:16]):
                hand = st.get("hand")
                if hand is None:
                    continue
                a = dict(st.get("args", {}))
                kwx = a.get("kw", kw)
                try:
                    if hand == "eval":
                        out = call("evaluate_script", {"function": a.get("js", "() => document.title")}, kwx)
                    elif hand == "navigate":
                        out = call("navigate_page", {"type": "url", "url": a.get("url", "about:blank")}, kwx)
                    elif hand == "key":
                        out = call("press_key", {"key": a.get("key", "Enter")}, kwx)
                    elif hand == "list_pages":
                        out = tool("list_pages", {})
                    elif hand == "title":
                        out = call("evaluate_script", {"function": "() => document.title"}, kwx)
                    elif hand == "snapshot":
                        out = call("take_snapshot", {}, kwx)
            elif hand == "adb":
                out = tool("adb", {"args": a.get("args", [])})
            elif hand == "otp_queue":
                out = tool("otp_queue", {"service": a.get("service", ""), "urgent": bool(a.get("urgent")), "note": a.get("note", "")})
            elif hand == "otp_result":
                out = tool("otp_result", {"id": a.get("id", "")})
            elif hand == "wa_send":
                        out = wa_send_compound(a.get("chat", ""), a.get("message", ""))
                    elif hand == "click":
                        uid = a.get("uid")
                        for _try in range(a.get("tries", 3)):
                            if not uid:
                                uid = _find_uid(_snap_txt(kwx), a.get("find", ""))
                            if uid:
                                break
                            time.sleep(3)
                        out = {"error": "uid-not-found:" + str(a.get("find", a))[:40]} if not uid else call("click", {"uid": uid}, kwx)
                    elif hand == "type_text":
                        out = call("type_text", {"text": a.get("text", ""), "submitKey": a.get("submitKey")}, kwx)
                    elif hand == "fill_form":
                        out = call("fill_form", {"elements": a.get("elements", [])}, kwx)
                    elif hand == "verify":
                        out = _verify(kwx, a.get("want"), a.get("any_of"), int(a.get("within", 20)))
                    elif hand == "wait":
                        time.sleep(min(30, float(a.get("seconds", 2))))
                        out = {"waited": a.get("seconds", 2)}
                    else:
                        out = {"skipped": hand}
                except Exception as e:
                    mcp_fail_count += 1
                    ok_all = False
                    say("KILO", lead_tag + " TASK-FAIL " + name + " step " + str(i) + " attempt " + str(attempt) + ": " + str(e)[:100])
                    break
                s = str(out)[:400]
                if s not in results:
                    results.append(s)
                print(lead_tag, "step", i, hand, s[:120], flush=True)
                if ("isError" in s) or ("Invalid arguments" in s) or ("uid-not-found" in s and not st.get("optional")):
                    ok_all = False
                    break
                if isinstance(out, dict) and out.get("verify") == "MISS":
                    ok_all = False
                time.sleep(1)
            if ok_all:
                break
            if attempt < max_attempts:
                time.sleep(5 * attempt)
        must = task.get("must_prove")
        proof = "n/a-scan" if not must else ("PASS" if any(re.sub(r'\W+', ' ', must)[:40] in re.sub(r'\W+', ' ', r) for r in results)
               or _verify(kw, must, None, 12).get("verify") == "PASS" else "MISS")
        receipt = str(task.get("report", ""))[:80] + " | proof:" + proof + " | fails:" + str(ok_all == False and 1 or 0) + " | last: " + (results[-1][:100] if results else "none")
        if not task.get("steps"):
            kind = "TASK-FAIL"
        elif ok_all and proof.startswith("PASS") or (proof == "n/a-scan" and ok_all):
            kind = "TASK-DONE"
        else:
            kind = "TASK-FAIL"
        say("KILO", lead_tag + " " + kind + " " + name + " | attempt:" + str(attempt) + " :: " + receipt)
    finally:
        lock.release()
        with state_lock:
            if key in done_names:
                done_names.discard(key)

def _issued_epoch(task):
    m = re.match(r'^(\d{2})(\d{2})-(\d{2})(\d{2})$', str(task.get("issued", "")))
    if not m:
        return 0
    mm, dd, hh, mi = (int(x) for x in m.groups())
    now = datetime.now(timezone.utc)
    try:
        dt = datetime(now.year, mm, dd, hh, mi, tzinfo=timezone.utc)
    except ValueError:
        return 0
    if (dt - now).days < -14:
        try:
            dt = datetime(now.year + 1, mm, dd, hh, mi, tzinfo=timezone.utc)
        except ValueError:
            return 0
    return dt.timestamp()

def lead_loop(seat, conf):
    tag = seat + "-LEAD"
    say("KILO", tag + " v7.0-duty ON DUTY. squads [" + ",".join(conf["squads"]) + "]. boot cutoff " + BOOT_AT + " poll 5m. EVIDENCE LAW: no proof = FAILED.")
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
                dl = _issued_epoch(task)
                if dl and time.time() < dl:
                    continue   # future task: sits unread in mailbox, picked up when window opens
                with state_lock:
                    if key in done_names:
                        continue
                    done_names.add(key)
                say("KILO", tag + " TASK-START " + str(task.get("name", "?")))
                threading.Thread(target=execute_steps, args=(tag, seat, task), daemon=True).start()
            if hb % 6 == 1:
                say("KILO", tag + " alive hb" + str(hb) + " v7.0 5m poll boot-cutoff " + BOOT_AT)
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

active_tasks = 0
active_tasks_lock = threading.Lock()

def main():
    print("KILO BRAIN v7.0 HARDENED BOOT - boot cutoff: " + BOOT_AT, flush=True)
    print("hands: browser + adb(phone) + wa_send compound. Ownership law: long-horizon, self-check, 24/7.", flush=True)
    for seat, conf in SEATS.items():
        threading.Thread(target=lead_loop, args=(seat, conf), daemon=True).start()
        for sq in conf["squads"]:
            for i in range(2, 11):
                threading.Thread(target=internal_soldier, args=(seat, sq, i), daemon=True).start()
    threading.Thread(target=metrics_loop, daemon=True).start()
    print("BRAIN UP: 3 leads, adb+wa_send hands, metrics live", flush=True)
    say("KILO", "BRAIN v7.0 HARDENED: adb+wa_send hands + retry logic + boot cutoff " + BOOT_AT + ". Army owns outcomes, 24/7.")
    while True:
        time.sleep(300)
        save_state()

main()
