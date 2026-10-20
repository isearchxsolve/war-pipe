# KILO WORKER v2 - SIMPLIFIED WORKER LOOP (no corpus build)
# Father's law 2026-09-11: ALL heavy work runs here. Laptop stays light.
# Jobs ride the relay ledger (body=KILO): JOB_START / JOB_CHUNK / JOB_RUN protocol.
# Results stream back: JOB_PROG / JOB_OUT / JOB_END / JOB_ERR. Files land in /kaggle/working/<jobid>/
# 5-minute poll (free quota law). WORKER_ALIVE heartbeat every 30 min. Skips already-done jobs on re-paste.
import os, sys, json, time, base64, hashlib, subprocess, urllib.request

TOK = "GOLD24"
DOORS = [
    "https://fathers-crowd-fraction-vatican.trycloudflare.com",
    "https://retrain-schnapps-upbeat.ngrok-free.dev",
    "https://demand-florist-allowance-basket.trycloudflare.com",
    "https://phantom-analytical-gains-curious.trycloudflare.com",
]
HDRS = {"User-Agent": "kilo-worker-kdas19999", "ngrok-skip-browser-warning": "1"}
POLL = 300          # 5m - free quota law
HEARTBEAT = 1800    # 30 min
STATE = "/kaggle/working/worker-state.json"
JOBS = "/kaggle/working/jobs"
os.makedirs(JOBS, exist_ok=True)

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

def say(text, retries=3):
    global C
    for attempt in range(retries):
        if not C:
            C = door()
            if not C:
                time.sleep(10)
                continue
        try:
            data = json.dumps({"body": "KILO", "text": text}).encode()
            req = urllib.request.Request(C + "/say?token=" + TOK, data=data, headers=HDRS)
            urllib.request.urlopen(req, timeout=30).read()
            return True
        except Exception:
            C = None
            time.sleep(5)
    return False

def fetch():
    global C
    if not C:
        C = door()
        if not C:
            return []
    try:
        req = urllib.request.Request(C + "/say?body=KILO&token=" + TOK + "&limit=60", headers=HDRS)
        return json.loads(urllib.request.urlopen(req, timeout=30).read().decode()).get("orders", [])
    except Exception:
        C = None
        return []

# state: seen message keys, finished jobs, partial assemblies
if os.path.exists(STATE):
    try:
        ST = json.load(open(STATE))
    except Exception:
        ST = {}
else:
    ST = {}
ST.setdefault("seen", [])
ST.setdefault("done", [])
ST.setdefault("parts", {})
seen = set(ST["seen"])
done = set(ST["done"])
parts = {k: v for k, v in ST["parts"].items()}

def save_state():
    ST["seen"] = list(seen)[-500:]
    ST["done"] = list(done)[-200:]
    ST["parts"] = parts
    json.dump(ST, open(STATE, "w"))

def run_job(jid):
    src_path = os.path.join(JOBS, jid + ".py")
    if not os.path.exists(src_path):
        say(f"JOB_ERR {jid} source missing")
        return
    meta = parts.get(jid + ":meta", {})
    timeout = int(meta.get("timeout", 3600))
    out_dir = os.path.join("/kaggle/working", jid)
    os.makedirs(out_dir, exist_ok=True)
    prelude = (
        "import os, sys, json, time, base64, urllib.request\n"
        f"TOK='{TOK}'; JOBID='{jid}'\n"
        "def kilo_report(msg):\n"
        "    try:\n"
        "        import json as _j, urllib.request as _u\n"
        "        doors=['https://fathers-crowd-fraction-vatican.trycloudflare.com','https://retrain-schnapps-upbeat.ngrok-free.dev','https://demand-florist-allowance-basket.trycloudflare.com','https://phantom-analytical-gains-curious.trycloudflare.com']\n"
        "        h={'User-Agent':'kilo-job','ngrok-skip-browser-warning':'1'}\n"
        "        for d in doors:\n"
        "            try:\n"
        "                data=_j.dumps({'body':'KILO','text':'JOB_PROG '+JOBID+' '+str(msg)}).encode()\n"
        "                _u.urlopen(_u.Request(d+'/say?token='+TOK, data=data, headers=h), timeout=20).read()\n"
        "                return\n"
        "            except Exception:\n"
        "                continue\n"
        "    except Exception:\n"
        "        pass\n"
    )
    full = open(src_path).read()
    with open(src_path, "w") as f:
        f.write(prelude + full)
    say(f"JOB_PROG {jid} running timeout={timeout}")
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, src_path], capture_output=True, text=True, timeout=timeout, cwd=out_dir)
        rc, outp, errp = r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        rc, outp, errp = 124, "", "TIMEOUT"
    tail = (outp[-8000:] + "\n--STDERR--\n" + errp[-4000:])[-10000:]
    b64 = base64.b64encode(tail.encode()).decode()
    chunks = [b64[i:i + 40000] for i in range(0, len(b64), 40000)] or [""]
    for i, ch in enumerate(chunks):
        say(f"JOB_OUT {jid} {i+1}/{len(chunks)}:{ch}")
        time.sleep(0.5)
    say(f"JOB_END {jid} rc={rc} secs={int(time.time()-t0)} out_dir={out_dir}")
    done.add(jid)

C = door()
print("worker door:", C, flush=True)
say(f"WORKER_ALIVE v2 ready - poll={POLL}s - jobs dir {JOBS} - account=kdas19999")
last_beat = time.time()
while True:
    orders = fetch()
    for o in orders:
        t = str(o.get("text", ""))
        key = str(o.get("at", "")) + ":" + hashlib.md5(t.encode()).hexdigest()[:8]
        if key in seen:
            continue
        seen.add(key)
        if t.startswith("JOB_START "):
            p = t.split()
            jid = p[1]
            if jid in done:
                say(f"JOB_SKIP {jid} already done")
            else:
                parts[jid] = {"n": int(p[2]), "sha": p[3], "chunks": {}}
                parts[jid + ":meta"] = {"timeout": int(p[4]) if len(p) > 4 else 3600}
                say(f"JOB_ACK {jid} expecting {p[2]} chunks")
        elif t.startswith("JOB_CHUNK "):
            head, b64 = t.split(":", 1)
            p = head.split()
            jid, idx = p[1], int(p[2].split("/")[0])
            if jid in parts and isinstance(parts[jid], dict) and "chunks" in parts[jid]:
                parts[jid]["chunks"][idx] = b64
                got = len(parts[jid]["chunks"])
                if got == parts[jid]["n"]:
                    full_b64 = "".join(parts[jid]["chunks"][i] for i in sorted(parts[jid]["chunks"]))
                    src = base64.b64decode(full_b64).decode()
                    ok_sha = hashlib.sha1(src.encode()).hexdigest() == parts[jid]["sha"]
                    src_path = os.path.join(JOBS, jid + ".py")
                    open(src_path, "w").write(src)
                    say(f"JOB_ASSEMBLED {jid} sha_ok={ok_sha} bytes={len(src)}")
                    parts.pop(jid)
                    save_state()
                    run_job(jid)
                else:
                    say(f"JOB_ACK {jid} chunk {idx} ({got}/{parts[jid]['n']})")
        save_state()
    if time.time() - last_beat > HEARTBEAT:
        say(f"WORKER_ALIVE heartbeat - uptime={int(time.time()-last_beat)+HEARTBEAT}s - account=kdas19999")
        last_beat = time.time()
        save_state()
    time.sleep(POLL)
