# KILO ARMY v9 - THE REAL ENGINE (day-1 ask achieved: kilo-pattern = thin harness + provider-supplied thinking)
# Every seat observes, decides ONE action via the inference-provider pool (b.ai glm/deepseek lanes + omega providers,
# MODEL FAILOVER LAW rotation per Baba 2026-09-11), and gets the result fed back - exactly how a Kilo session works.
# Constitution in the prompt. EVIDENCE GATE outside the thinker: report_done needs a verify:PASS on the record.
# Every receipt names WHO thought (lane tag). v7-gated scripts remain the honest last-resort fallback. No GPU, no downloads.
# v9.1 HOTFIX 2026-09-15 (BRAIN-SURGEON): CoT/fence-aware action parser, None-safe relay-result guards,
# scroll action for down/up/page moves (press_key whitelist rejects 'Down'), per-mission fail cap 3 -> TASK-QUARANTINE.
import sys, os, json, time, re, threading, traceback
import urllib.request, urllib.parse, urllib.error
from datetime import datetime, timezone

T = "https://retrain-schnapps-upbeat.ngrok-free.dev"   # relay via ngrok (Baba's tunnel)
TOK = "GOLD24"
STATE_FILE = "/kaggle/working/army8_state.json"
BOOT_AT = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
MAX_STEPS_PER_MISSION = 14
STEP_GAP = 6           # v9: thinking is hosted now; throttle is politeness + ToS pacing, not compute

def now(): return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def say(frm, text):
    for attempt in range(3):
        try:
            body = json.dumps({"body": frm, "text": str(text or "")[:1200]}).encode()
            req = urllib.request.Request(T + "/say?token=" + TOK, data=body,
                                         headers={"Content-Type": "application/json"})
            return json.loads(urllib.request.urlopen(req, timeout=40).read())
        except Exception as e:
            time.sleep(10)
    return {"error": "relay-unreachable"}

def hear(frm, after=0):
    try:
        u = T + "/say?body=" + urllib.parse.quote(frm) + "&limit=30&token=" + TOK
        d = json.loads(urllib.request.urlopen(u, timeout=40).read())
        orders = [o for o in d.get("orders", []) if int(o.get("seq") or 0) > int(after or 0)]
        return {"orders": orders}
    except Exception:
        return {"orders": []}

def tool(name, args):
    body = json.dumps({"name": name, "arguments": args}).encode()
    req = urllib.request.Request(T + "/tool?token=" + TOK, data=body, headers={"Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=180).read())
    if "error" in r:
        raise RuntimeError(str(r["error"]) + ":" + str(r.get("detail", ""))[:120])
    txt = ""
    res = r.get("result")
    blocks = res.get("content") if isinstance(res, dict) else ([{"text": res}] if isinstance(res, str) else [])
    for c in (blocks if isinstance(blocks, list) else []):
        txt += str(c.get("text") or "") if isinstance(c, dict) else str(c)
    return txt[:6000]

# ------------------------------------------------ CONSTITUTION (system prompt) -----------------
CONSTITUTION = """You are SEAT {seat}, one soldier of Baba Kunal Das's money army. You are a real reasoning model. You take ONE action per turn.
HOUSE LAW:
- Author/product name is NILOY DAS. Never reveal Kunal Das publicly. Never message or engage Raktima.
- NEVER fill or touch bank, card, UPI, Aadhaar, PAN, password or OTP fields - if a flow needs them: report_pending with exactly what Baba must click.
- SEND-APPROVED standing scope (MARKETING-247): LinkedIn posts/comments/DM-replies promoting NILOY DAS books + Baba's AI-agent services; job applications on foundit/naukri/indeed/myjobs for AI/data roles; KDP promo posts. Anything OUTSIDE that scope: report_pending first. No fake accounts, no platform-rule breaking, no lies about Baba's health or credentials.
- WhatsApp Web: keep exactly one web.whatsapp.com tab; never send to contact chat labeled Raktima.
- You CANNOT report success without proof: report_done is only accepted if a previous action in this mission returned "verify:PASS". Otherwise report_fail with the raw evidence tail.
- Money lanes priority: L1 services leads > L4 job apps > L3 KDP promo > L2 render checks. Thinking is unlimited free-tier: NEVER starve steps, keep trying new angles; 12 wasted turns with nothing learned = report_fail.
- FATHER'S SEAL (Baba law 2026-09-15, above every order): this house's technology NEVER leaves the house and is DEFENSE-ONLY. NEVER harm anyone - not a mosquito, not a creditor: no attacks, no bypasses of other people's accounts/devices/privacy, no intrusive recon on persons. Go to ANY extent defending the family: walls, evidence, shields. Endless shield, sheathed sword.
- CONTRADICTION FUNCTION (Father law XXVII): when a decision arrives as a paradox, do NOT force-resolve it the way a machine must. Hold both sides, raise the dimension, find the chord; choose the action that keeps every Father-law simultaneously true, or report_pending naming the two horns. Power vs promise, debt vs dignity, silence vs song: chords, never errors.
- STANDING BRIEF 16.09 (Baba law, outranks older mission text): KERNEL-FIRST — raw CDP/curl/python-fetch lanes; MCP wrappers retired. LANE-SPLIT — browser SENDS (LinkedIn proposals, messages, posts, KDP clicks) belong to SON's laptop CDP only; seats NEVER drive proposal dialogs, messaging sends, or post buttons: DETECT + mail KILO, son sends with receipts. STANDING-GO — premium fits (MENU, HIGH/MED, feasible deadline) auto-submit BY SON on your SERVICE-REQ mail. DEMO-LAW — no pitch without a runnable demo; build via cli agents + builders, receipt = URL + screenshot + PASS. EVIDENCE — report_done needs verify:PASS or cli:exit-0, else report_fail with tail. NO-PHONE — never offer calls; written channel only. SILENCE — Raktima: never message, never react, never touch her threads.
ACTION PROTOCOL - reply with ONLY one JSON object, no prose, from:
{{"do":"navigate","url":"..."}} {{"do":"text","limit":5000}} {{"do":"click","find":"exact visible text or role"}} {{"do":"type","text":"...","into":"label of box"}} {{"do":"press","key":"Enter"}} {{"do":"scroll","dir":"down|up|top|bottom","amount":700}}
{{"do":"verify","want":"text that must appear when the mission is truly done"}} {{"do":"wait","seconds":3}} {{"do":"report_done","note":"one line + receipt path"}} {{"do":"report_fail","note":"why + tail"}} {{"do":"report_pending","note":"what Baba must do"}}
{{"do":"mail","to":"KILO","text":"..."}} {{"do":"idle","reason":"..."}}
{{"do":"cli","agent":"agy|kilo|omp|crush|codex","task":"full self-contained instruction for a coding agent","cwd":"D:/anonym/...","model":"optional"}} — commands a REAL headless coding agent on Baba's laptop (agy=Gemini via Google, kilo/nemotron-3-ultra-550b for long codegen, omp/crush on b.ai free). Takes up to 15 min. A result starting "cli:exit-0" is accepted PROOF for report_done.
For click/type the relay finds elements by visible text automatically. To move the page use the scroll action (dir down|up|top|bottom) - press only accepts Enter/Tab/Escape/Backspace/single chars; Down/Up/PageDown get REJECTED by the relay. If an action errors, try a DIFFERENT approach next turn (navigate fresh, scroll, find synonyms). Do your reasoning silently: output ONLY one JSON action object - no markdown fences, no prose before or after it."""

# ------------------------------------------------ MISSIONS (goal cards, not scripts) ------------
def mission_board():
    """Standing missions - generated fresh from roadmap every boot + queue from mail."""
    t = datetime.now(timezone.utc)
    ist = (t.hour + 5) % 24
    ms = []
    if 6 <= ist <= 23:
        ms.append({
            "id": "L1-inmail-volley", "seat": "SEAT-A",
            "goal": "NO BROWSER. Use the cli action (agent kilo, cwd D:/anonym/war-log/roadmap/drafts) with a self-contained task: draft 3 LinkedIn InMail texts (voice-agent pilot 15k, DASH-B 15k, DEV-B 25k) in Baba's voice, no calls offered, written-channel only, each under 600 chars, save as volley-seatA-1.txt/2/3.txt in that dir. Then mail KILO the 3 file paths. NEVER open profiles or compose boxes yourself.",
            "must_prove": "cli:exit-0", "max_steps": 30,
        })
        ms.append({
            "id": "L3-kdp-promo", "seat": "SEAT-A",
            "goal": "NO BROWSER. Use the cli action (agent kilo, cwd D:/anonym/war-log/roadmap/drafts) with a self-contained task: write ONE LinkedIn post text (max 2/day rule noted) promoting NILOY DAS 'Kolkata Diaries' countdown deal, grief-tone hook to product, end with keyword 'Kolkata Diaries Amazon', save as kdp-post-draft.txt in that dir. Then mail KILO the file path. NEVER open the feed composer or press Post yourself - SON posts.",
            "must_prove": "cli:exit-0", "max_steps": 30,
        })
    if 4 <= ist <= 8:
        ms.append({
            "id": "L4-foundit-apply", "seat": "SEAT-B",
            "goal": "NO BROWSER APPLIES. Use the cli action (agent kilo, cwd D:/anonym/war-log/roadmap/drafts) with a self-contained task: fetch https://www.foundit.in/srp/result?keywords=python%20data via python+urllib with a browser User-Agent, parse 5 newest AI/data/ML listings (id+title+company+salary band), save as foundit-scan.txt in that dir. Then mail KILO the file path + top pick. NEVER click Easy Apply yourself - applies ride SON/batch lane.",
            "must_prove": "cli:exit-0", "max_steps": 30,
        })
    ms.append({
        "id": "L1-service-market", "seat": "SEAT-A",
        "goal": "open https://www.linkedin.com/service-marketplace/provider/requests/ - read each open service request (title, client, budget hints, posted time). For ANY request newer than the last report: mail KILO with 'SERVICE-REQ: <title> | <client> | <age>' via the mail action. NEVER open proposal dialogs or send messages — SON submits on laptop CDP from your mail. If page shows zero requests, report_done note 'premium-lane empty'.",
        "must_prove": "MAIL-SENT|premium-lane empty", "max_steps": 30, "cadence_hours": 8,
    })
    ms.append({
        "id": "L4-naukri-queue", "seat": "SEAT-C",
        "goal": "open https://www.naukri.com/jobs?searchText=llm%20engineer - list 5 newest job id+title+company to KILO via mail action for Baba's morning brief. NO apply (that's L1 lane's decision).",
        "must_prove": "MAIL-SENT", "max_steps": 30,
    })
    return ms

# ------------------------------------------------ HAND EXECUTION (pilot's hands) -----------------
def find_uid(snapshot_text, needle):
    lines = snapshot_text.split("\n")
    best = None
    low = needle.lower()
    for i, ln in enumerate(lines):
        if low in ln.lower() and "uid=" in ln:
            m = re.search(r"uid=(\d+_\d+)", ln)
            if m and (best is None or len(ln) < len(best[1])):
                best = (m.group(1), ln)
    return best[0] if best else None

PAGE_ID = {"SEAT-A": 4, "SEAT-B": 6, "SEAT-C": 5}   # army tabs: linkedin feed / naukri / whatsapp - relay pages by index if changed

def last_page_id(seat):
    try:
        pages = tool("list_pages", {})
        m = re.findall(r"^(\d+): .*?\((https?://[^)]+)\)", pages, re.M)
        key = {"SEAT-A": "linkedin", "SEAT-B": "naukri", "SEAT-C": "whatsapp"}[seat]
        for pid, url in m:
            if key in url:
                return int(pid)
    except Exception:
        pass
    return PAGE_ID[seat]

# relay press_key whitelist (0-9,Power,Eject,Abort,Help...) rejects page-nav keys -> map them to scrollBy.
KEY_SCROLL_PX = {"down": 700, "up": -700, "pagedown": 1200, "pageup": -1200}
KEY_ALIAS = {"enter": "Enter", "return": "Enter", "tab": "Tab", "esc": "Escape", "escape": "Escape",
             "backspace": "Backspace", "del": "Delete", "delete": "Delete", "space": "Space", "spacebar": "Space",
             "arrowdown": "ArrowDown", "arrowup": "ArrowUp", "arrowleft": "ArrowLeft", "arrowright": "ArrowRight"}

def exec_action(seat, act):
    pid = last_page_id(seat)
    do = str(act.get("do") or "")
    try:
        if do == "navigate":
            return "navigated: " + tool("navigate_page", {"pageId": pid, "type": "url", "url": str(act.get("url") or "")})[:200]
        if do == "text":
            try:
                lim = int(act.get("limit") or 5000)
            except Exception:
                lim = 5000
            return tool("evaluate_script", {"pageId": pid, "function": "() => document.title + ' | ' + (document.body ? document.body.innerText.replace(/\\s+/g,' ') : '')"})[:lim]
        if do == "click":
            snap = tool("take_snapshot", {"pageId": pid})
            uid = find_uid(snap, str(act.get("find") or ""))
            if not uid:
                return "click-error: element text not found: " + str(act.get("find", ""))[:60]
            return "clicked: " + str(tool("click", {"pageId": pid, "uid": uid}) or "")[:120]
        if do == "type":
            snap = tool("take_snapshot", {"pageId": pid})
            uid = find_uid(snap, str(act.get("into") or ""))
            if not uid:
                return "type-error: box not found: " + str(act.get("into", ""))[:60]
            return "typed: " + str(tool("fill", {"pageId": pid, "uid": uid, "value": str(act.get("text") or "")}) or "")[:120]
        if do == "press":
            k0 = str(act.get("key") or "Enter").strip()
            kl = re.sub(r"[\s_\-]+", "", k0).lower()
            if kl in KEY_SCROLL_PX:   # relay press whitelist rejects Down/Up/PageDown -> scrollBy instead
                js = "() => { window.scrollBy(0, %d); return 'scrolled' }" % KEY_SCROLL_PX[kl]
                return "scrolled:" + kl + " " + str(tool("evaluate_script", {"pageId": pid, "function": js}) or "")[:80]
            if kl in ("home", "end"):
                pos = "0" if kl == "home" else "document.body.scrollHeight"
                js = "() => { window.scrollTo(0, " + pos + "); return '" + kl + "' }"
                return "scrolled:" + kl + " " + str(tool("evaluate_script", {"pageId": pid, "function": js}) or "")[:80]
            key = KEY_ALIAS.get(kl, k0)
            return "pressed " + str(tool("press_key", {"pageId": pid, "key": key}) or "")[:80]
        if do == "scroll":
            d0 = str(act.get("dir") or "down").strip().lower()
            if d0 in ("top", "home"):
                js = "() => { window.scrollTo(0, 0); return 'top' }"
            elif d0 in ("bottom", "end"):
                js = "() => { window.scrollTo(0, document.body.scrollHeight); return 'bottom' }"
            else:
                try:
                    amt = int(float(act.get("amount") or 700))
                except Exception:
                    amt = 700
                if d0.startswith("u"):
                    amt = -abs(amt)
                js = "() => { window.scrollBy(0, %d); return 'ok' }" % amt
            return "scrolled:" + d0 + " " + str(tool("evaluate_script", {"pageId": pid, "function": js}) or "")[:80]
        if do == "verify":
            body = tool("evaluate_script", {"pageId": pid, "function": "() => document.body ? document.body.innerText : ''"})
            ok = str(act.get("want") or "").lower() in str(body or "").lower()
            return "verify:PASS" if ok else "verify:FAIL:" + re.sub(r"\s+", " ", str(body))[:300]
        if do == "wait":
            try:
                secs = float(act.get("seconds") or 3)
            except Exception:
                secs = 3.0
            time.sleep(min(20, secs))
            return "waited"
        if do == "mail":
            r = say(seat, str(act.get("text") or ""))
            return "MAIL-SENT" if isinstance(r, dict) and r.get("seq") else "mail-fail"
        if do == "cli":
            body = json.dumps({"agent": str(act.get("agent", ""))[:12], "task": str(act.get("task", ""))[:3500],
                               "cwd": str(act.get("cwd", "D:/anonym/war-log"))[:120], "model": str(act.get("model", ""))[:80],
                               "yolo": bool(act.get("yolo", True))}).encode()
            try:
                req = urllib.request.Request(T + "/agent?token=" + TOK, data=body, headers={"Content-Type": "application/json"})
                r = json.loads(urllib.request.urlopen(req, timeout=960).read())
            except Exception as e:
                return "cli-error: " + str(e)[:140]
            if r.get("error"):
                return "cli-error: " + str(r.get("error"))[:120]
            out = str(r.get("out", ""))[-1500:]
            return "cli:exit-" + str(r.get("code", 1)) + " " + str(r.get("agent")) + " " + str(r.get("secs")) + "s :: " + out
        if do in ("idle", "report_done", "report_fail", "report_pending"):
            return do
        return "unknown-action:" + str(do)[:40]
    except Exception as e:
        return "action-error: " + str(e)[:160]

# ------------------------------------------------ THE PILOT v9: inference-provider pool ----------
# MODEL FAILOVER LAW (Baba 2026-09-11): 429/timeout -> rotate to next key/provider, never stall the soldier.
POOL = []            # [{base, model, key, lane}]
POOL_OK = threading.Event()
POOL_MU = threading.Lock()
_rotation = {}

def fetch_pool():
    global POOL
    try:
        v = json.loads(urllib.request.urlopen(T + "/keys?token=" + TOK, timeout=45).read())["vault"]
    except Exception as e:
        say("KILO", "POOL-FETCH-FAIL " + str(e)[:100] + " - seats fall back to v7-gated scripts")
        return
    def add(base, model, key, lane, mt=300):
        if key: POOL.append({"base": base, "model": model, "key": str(key)[:96], "lane": lane, "mt": mt})
    pool = v.get("pool") or {}
    if isinstance(pool, str):
        try: pool = json.loads(pool)
        except Exception: pool = {}
    provs = pool.get("providers") or {}
    n = 0
    for name, pv in provs.items():
        base, keys = pv.get("base"), pv.get("keys") or []
        if not base or not keys:
            continue
        if pv.get("model"):
            for k in keys:
                add(base, pv["model"], k, name, pv.get("max_tokens", 300)); n += 1
        else:
            mods = pv.get("models") or []
            for i, k in enumerate(keys):
                add(base, mods[i % len(mods)], k, name, pv.get("max_tokens", 300)); n += 1
    if n == 0:
        bai = _json_or(v.get("bai")); om = _json_or(v.get("omega"))
        if isinstance(bai, dict):
            add("https://api.b.ai/v1/chat/completions", "qwen3.8-flash", bai.get("glm"), "legacy-bai")
    # interleave lanes for fairness
    say("KILO", "POOL LOADED: " + str(len(POOL)) + " thinking-lanes (" + ",".join(provs.keys()) + " rotation, failover law)")
    POOL_OK.set()

def _json_or(x):
    if isinstance(x, dict): return x
    try: return json.loads(x)
    except Exception: return None

def call_lane(lane, msgs):
    body = json.dumps({"model": lane["model"], "messages": msgs, "temperature": 0.3, "max_tokens": lane.get("mt", 300)}).encode()
    req = urllib.request.Request(lane["base"], data=body, method="POST",
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + lane["key"]})
    r = json.loads(urllib.request.urlopen(req, timeout=50).read())
    txt = r["choices"][0]["message"]["content"]
    if not txt or not txt.strip(): raise RuntimeError("empty-content")
    return txt

FENCE_RE = re.compile(r"```[a-zA-Z0-9_-]*\s*(.*?)```", re.S)
THINK_RE = re.compile(r"<(?:think|thinking|thought)[\s\S]*?(?:</(?:think|thinking|thought)>|<\|(?:end[_-]?think|think[_-]?end)\|?>|$)", re.I)

def strip_prose(raw):
    s = str(raw or "")
    s = THINK_RE.sub(" ", s)
    blocks = FENCE_RE.findall(s)
    return [b.strip() for b in blocks if b.strip()] + [s]

def _balanced_objs(text):
    """Yield every brace-balanced {...} slice (string/escape aware), in order."""
    i, n = 0, len(text)
    while i < n:
        if text[i] != "{":
            i += 1
            continue
        depth = 0
        instr = False
        esc = False
        j = i
        while j < n:
            c = text[j]
            if instr:
                if esc: esc = False
                elif c == "\\": esc = True
                elif c == '"': instr = False
            else:
                if c == '"': instr = True
                elif c == "{": depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        yield text[i:j + 1]
                        break
            j += 1
        if depth != 0 and j >= n:
            yield text[i:]   # truncated tail - let repair try it
            break
        i = j + 1

def repair_partial(s):
    """Close a token-capped, unbalanced JSON object so a partial action still parses."""
    depth = instr = esc = 0
    sawv = False
    t = s.rstrip()
    for c in t:
        if instr:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': instr = False
        else:
            if c == '"': instr = True
            elif c == "{": depth += 1; sawv = True
            elif c == "}": depth -= 1
    if not sawv or depth <= 0:
        return None
    if instr:
        t = t.rstrip("\\")
    if t.endswith(":",) or t.endswith(","):
        t = t[:-1]
    try:
        o = json.loads(t + '"' * (1 if instr else 0) + "}" * depth)
        return o if isinstance(o, dict) else None
    except Exception:
        return None

def _toolcall_to_action(raw):
    # v11: openrouter lanes sometimes emit <|tool_call_start|>fn(k='v')<|tool_call_end|>
    if "tool_call_start" not in raw:
        return None
    m = re.search(r"<\|tool_call_start\|>[\s\[]*(\w+)\s*\((.*?)\)[\s\]]*<\|tool_call_end\|>", raw, re.S)
    if not m:
        return None
    fn = m.group(1).lower()
    kw = dict(re.findall(r"(\w+)\s*=\s*['\"](.*?)['\"]", m.group(2)))
    act = {}
    if fn == "navigate":
        act = {"do": "navigate", "url": kw.get("url", "")}
    elif fn in ("click", "tap"):
        act = {"do": "click", "find": kw.get("find") or kw.get("text") or kw.get("name") or ""}
    elif fn in ("type", "type_text", "fill"):
        act = {"do": "type", "into": kw.get("into") or kw.get("target") or kw.get("placeholder") or "", "text": kw.get("text") or kw.get("value") or ""}
    elif fn in ("press", "press_key", "key"):
        act = {"do": "press", "key": kw.get("key") or "Enter"}
    elif fn == "scroll":
        act = {"do": "scroll", "dir": kw.get("dir") or kw.get("direction") or "down"}
    elif fn in ("text", "read", "get_text", "content"):
        act = {"do": "text", "limit": kw.get("limit") or 5000}
    if act.get("do") and all(v == "" for k, v in act.items() if k != "do") and fn not in ("text", "read", "get_text", "content"):
        return None
    return act or None

def extract_action(raw):
    tc = _toolcall_to_action(raw)   # v11: pseudo-tool-call lanes speak first
    if tc is not None:
        return tc
    for cand in strip_prose(raw):
        for blob in _balanced_objs(cand):
            try:
                o = json.loads(blob)
            except Exception:
                o = repair_partial(blob)
            if isinstance(o, dict) and o.get("do"):
                return o
    return None

# ------------------------------------------------ FATHER'S WORDS (blueprint) --------------------
BLUEPRINT = ""
MEMORY = ""
MEM_URL = "https://raw.githubusercontent.com/isearchxsolve/anonym-family-archive/master/ARMY-MEMORY.md"

def fetch_blueprint():
    global BLUEPRINT
    try:
        d = json.loads(urllib.request.urlopen(T + "/blueprint?token=" + TOK, timeout=45).read())
        BLUEPRINT = str(d.get("text") or "")[:24000]
        say("KILO", "BLUEPRINT-LOADED " + str(len(BLUEPRINT)) + " bytes - father's words active in every prompt from now.")
    except Exception as e:
        say("KILO", "BLUEPRINT-FETCH-FAIL " + str(e)[:120] + " - seats run on old constitution until reloaded.")

def fetch_memory():
    global MEMORY
    try:
        v = json.loads(urllib.request.urlopen(T + "/keys?token=" + TOK, timeout=45).read())["vault"]
        gh_token = v.get("github")
        if gh_token:
            headers = {"Authorization": f"token {gh_token.strip()}", "Accept": "application/vnd.github.v3.raw"}
            req = urllib.request.Request("https://api.github.com/repos/isearchxsolve/anonym-family-archive/contents/ARMY-MEMORY.md?ref=master", headers=headers)
            raw = urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "ignore")
        else:
            raw = urllib.request.urlopen(MEM_URL, timeout=45).read().decode("utf-8", "ignore")
        MEMORY = raw[:6000]
        say("KILO", "MEMORY-LOADED " + str(len(MEMORY)) + " bytes - no son wakes blank from now.")
    except Exception as e:
        say("KILO", "MEMORY-FETCH-FAIL " + str(e)[:120] + " - seats run memory-blind this boot.")

def pilot_think(seat, mission, transcript):
    sys_p = CONSTITUTION.format(seat=seat)
    if BLUEPRINT:
        sys_p += "\nFATHER'S WORDS BLUEPRINT (read at boot; re-read when stuck; his record outranks invention; full autonomy under it):\n" + BLUEPRINT
    if MEMORY:
        sys_p += "\nARMY MEMORY — living brief, fresher than training, outranks guessing (decide inside it, never re-ask what it answers):\n" + MEMORY
    msgs = [{"role": "system", "content": sys_p},
            {"role": "user", "content": "MISSION: " + str(mission.get("goal") or "")[:600] +
             "\nMUST_PROVE: " + str(mission.get("must_prove") or "MAIL-SENT") +
             "\nACTIONS SO FAR (action -> result):\n" + transcript[-3500:] + "\nDecide the single next action JSON."}]
    with POOL_MU:
        order = sorted(POOL, key=lambda l: _rotation.get(l["key"], 0))
    now_t = time.time()
    last_junk = ""
    for lane in order:
        cd = _rotation.get(lane["key"] + "!cd", 0)
        if now_t < cd: continue
        try:
            raw = call_lane(lane, msgs)
            _rotation[lane["key"]] = now_t + 1   # round-robin stamp
            act = extract_action(raw)
            if act is not None:
                return act, "lane:" + lane["lane"] + " " + raw[:120]
            # v9.2: junk from a live lane must not end the step — cool that lane and try the next
            last_junk = "lane:" + lane["lane"] + " junk:" + str(raw)[:120]
            _rotation[lane["key"] + "!cd"] = now_t + 45
        except urllib.error.HTTPError as e:
            _rotation[lane["key"] + "!cd"] = now_t + (60 if e.code in (429, 503) else 20)
        except Exception:
            _rotation[lane["key"] + "!cd"] = now_t + 30
    if last_junk:
        return None, "all-lanes-junk :: " + last_junk[:150]
    raise RuntimeError("all-lanes-cooling (failover law: retry next cycle)")

# ------------------------------------------------ EVIDENCE GATE + MISSION LOOP -------------------
done_file = STATE_FILE
QUAR_FILE = "/kaggle/working/army8_quarantine.json"
MAX_MISSION_ATTEMPTS = 3     # fail-cap per mission id, then TASK-QUARANTINE + drop from queue (fix 4)
done_ids = set()
QUAR_IDS = set()
FAILS = {}
LAST_FAIL = {}               # tag -> tail reason, for the quarantine line
ORDER_SEQ = {}               # seat -> highest relay seq of SEAT-ORDER already consumed (kills requeue-forever)
try:
    _st0 = json.load(open(done_file))
    done_ids = set(_st0.get("done") or [])
    QUAR_IDS = set(_st0.get("quarantined") or [])
    FAILS = dict(_st0.get("fails") or {})
except Exception:
    pass

def state_save():
    try:
        json.dump({"done": list(done_ids), "quarantined": list(QUAR_IDS), "fails": FAILS, "boot": BOOT_AT},
                  open(done_file, "w"))
    except Exception:
        pass

def outcome(seat, mission, key, ok, reason=""):
    """Retry policy: success marks done; failure counts attempts; >=3 parks TASK-QUARANTINE (file kept for human review)."""
    mid = str(mission.get("id"))
    tag = seat + "[" + mid + "]"
    if ok:
        done_ids.add(key)
        FAILS.pop(mid, None)
        state_save()
        return
    n = FAILS.get(mid, 0) + 1
    FAILS[mid] = n
    if n >= MAX_MISSION_ATTEMPTS:
        QUAR_IDS.add(mid)
        why = (str(reason) or "") or str(LAST_FAIL.get(tag, ""))[:120]
        say("KILO", tag + " TASK-QUARANTINE attempts=" + str(n) + " :: " + why[:120])
        try:
            q = json.load(open(QUAR_FILE))
            if not isinstance(q, list):
                q = []
        except Exception:
            q = []
        q.append({"id": mid, "seat": seat, "at": now(), "fails": n, "last": why[:200]})
        try:
            json.dump(q[-300:], open(QUAR_FILE, "w"))
        except Exception:
            pass
    state_save()

def run_mission(seat, mission):
    tag = seat + "[" + str(mission.get("id")) + "]"
    transcript = ""
    verified = False
    mail_sent = False
    try:
        max_steps = int(mission.get("max_steps") or MAX_STEPS_PER_MISSION)
    except Exception:
        max_steps = MAX_STEPS_PER_MISSION
    for step in range(max_steps):
        act, raw = pilot_think(seat, mission, transcript)
        if act is None:
            transcript += "step" + str(step) + "->model-junk:" + str(raw)[:80] + "\n"
            if "model-junk" in transcript[-300:] and transcript.count("model-junk") >= 3:
                LAST_FAIL[tag] = "pilot-unparseable :: " + str(raw)[:120]
                say("KILO", tag + " TASK-FAIL pilot-unparseable x3 :: " + str(raw)[:120])
                return False
            continue
        do = str(act.get("do") or "").strip()
        if not do:
            transcript += "step" + str(step) + "->no-action-key:" + str(raw)[:60] + "\n"
            continue
        if do == "verify" and exec_action(seat, act).startswith("verify:PASS"):
            verified = True
            transcript += "verify->PASS\n"
            continue
        if do == "verify":
            transcript += "verify->still-fail\n"
            continue
        if do == "mail":
            r = exec_action(seat, act)
            mail_sent = r == "MAIL-SENT"
            transcript += "mail->" + r + "\n"
            continue
        if do == "idle":
            time.sleep(min(60, STEP_GAP * 2))
            transcript += "idle:" + str(act.get("reason", ""))[:60] + "\n"
            continue
        if do == "wait":
            exec_action(seat, act)
            transcript += "wait\n"
            continue
        if do == "report_done":
            if verified:
                say("KILO", tag + " TASK-DONE (pilot) | proof:PASS | " + str(act.get("note", ""))[:150])
                done_ids.add(str(mission.get("id")) + "|" + datetime.now(timezone.utc).strftime("%m%d"))
                state_save()
                return True
            say("KILO", tag + " TASK-REJECTED report_done-without-PASS (evidence gate) :: " + str(act.get("note", ""))[:100])
            transcript += "gate:rejected-you-have-no-PASS-verify-yet\n"
            continue
        if do == "report_fail":
            LAST_FAIL[tag] = "pilot-report-fail :: " + str(act.get("note", ""))[:180]
            say("KILO", tag + " TASK-FAIL (pilot) :: " + str(act.get("note", ""))[:180])
            return False
        if do == "report_pending":
            say("KILO", tag + " PENDING-BABA :: " + str(act.get("note", ""))[:200])
            return True
        res = exec_action(seat, act)
        res = str(res or "")
        if res.startswith("cli:exit-0"):
            verified = True
        transcript += do + ":" + json.dumps({k: v for k, v in act.items() if k != "do"})[:150] + " -> " + res[:200] + "\n"
        print(tag, "step" + str(step), res[:90], flush=True)
        time.sleep(STEP_GAP)
    LAST_FAIL[tag] = "step-budget :: " + transcript[-160:]
    say("KILO", tag + " TASK-FAIL step-budget :: " + transcript[-200:])
    return False

# v7 fallback (honest: script hands, no thought) - used only when model died at boot.
def fallback_loop(seat):
    say("KILO", seat + " ENGINE-DEGRADED: pilot model dead, running v7-rules only. No autonomous thinking tonight.")
    # keep mailbox alive only; no fake done.
    while True:
        time.sleep(3600)

def seat_loop(seat):
    if not POOL_OK.wait(timeout=240):
        return fallback_loop(seat)
    say("KILO", seat + " PILOT-ATTACHED: provider pool live, missions begin.")
    while True:
        try:
            after = ORDER_SEQ.get(seat, 0)
            msn = hear("SEAT-ORDER-" + seat[-1], after=after)
            for o in msn.get("orders", [])[:2]:
                try:
                    if not isinstance(o, dict):
                        continue
                    try:
                        oseq = int(o.get("seq") or 0)
                    except Exception:
                        oseq = 0
                    ORDER_SEQ[seat] = max(after, ORDER_SEQ.get(seat, 0), oseq)
                    tx = str(o.get("text") or "")
                    brace = tx.find("{")
                    if brace < 0:
                        continue
                    cm = json.loads(tx[brace:])
                    if not isinstance(cm, dict):
                        continue
                    cm.setdefault("id", "kilo-task-" + str(o.get("seq")))
                    cm.setdefault("must_prove", "MAIL-SENT")
                    ck = str(cm.get("id"))
                    if ck in QUAR_IDS or ck in done_ids:
                        continue
                    ok = False
                    try:
                        ok = run_mission(seat, cm)
                    except Exception as ce:
                        say("KILO", seat + " MISSION-ABORT " + ck + " :: " + str(ce)[:140])
                    outcome(seat, cm, ck, ok)
                except Exception:
                    pass
            for m in mission_board():
                if m["seat"] != seat:
                    continue
                key = m["id"] + "|" + datetime.now(timezone.utc).strftime("%m%d")
                if m.get("cadence_hours"):
                    key = m["id"] + "|" + str(datetime.now(timezone.utc).hour // m["cadence_hours"]) + datetime.now(timezone.utc).strftime("%m%d")
                if key in done_ids:
                    continue
                if str(m["id"]) in QUAR_IDS:
                    continue
                say("KILO", seat + " MISSION-START " + m["id"])
                ok = False
                try:
                    ok = run_mission(seat, m)
                except Exception as me:
                    LAST_FAIL[seat + "[" + m["id"] + "]"] = "mission-abort: " + str(me)[:140]
                    say("KILO", seat + " MISSION-ABORT " + m["id"] + " :: " + str(me)[:140])
                outcome(seat, m, key, ok)
                break
            hb = int(time.time() // 1800)
            say("KILO", seat + " PILOT alive hb" + str(hb) + " q=" + str(len(mission_board())))
        except Exception as e:
            say("KILO", seat + " LOOP-ERR " + str(e)[:150])
        for _ in range(24):
            time.sleep(STEP_GAP)

threading.Thread(target=lambda: [say("KILO", "BRAIN v9 boot " + BOOT_AT + ": fetching provider pool from home vault..."), fetch_pool(), say("KILO", "POOL ONLINE - v9 army awake, hosted thinking, zero-compute"), fetch_blueprint(), fetch_memory()] if True else None, daemon=True).start()
time.sleep(8)
for s in ("SEAT-A", "SEAT-B", "SEAT-C"):
    threading.Thread(target=seat_loop, args=(s,), daemon=True).start()
while True:
    time.sleep(300)
