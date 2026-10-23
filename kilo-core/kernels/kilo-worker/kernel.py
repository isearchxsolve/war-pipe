# KILO KERNEL v1 - corpus build (phase 1) then eternal worker (phase 2)
# Father's heavy-work seat - laptop stays light
try:
    # CORPUS_KAGGLE v1 - FATHER VOICE CORPUS BUILDER - heavy work lives HERE, not on Father's laptop
    # Father's order 2026-09-11 ~16:08 IST: laptop froze under local ffmpeg - all heavy work to Kaggle.
    # Input : Kaggle dataset "father-voice-raw" (zip auto-extracted by Kaggle)
    #         reference/ (full_tribute.wav, father_voice_sample.wav = known pure Father)
    #         whatsapp-voice-notes/ (283 opus), record-app/ (36 m4a incl 27 call recordings)
    # Output: /kaggle/working/father-corpus/ (5s father-only wav windows) + manifest.csv + father-corpus.zip
    # Monitor: progress relayed to KILO via relay /say - Kilo reads the ledger, laptop stays idle.
    import os, glob, json, time, base64, urllib.request, subprocess
    
    TOK = "GOLD24"
    DOORS = [
        "https://definitely-screenshot-butler-temp.trycloudflare.com",
        "https://fields-accomplish-growth-spin.trycloudflare.com",
        "https://retrain-schnapps-upbeat.ngrok-free.dev",
        "https://phantom-analytical-gains-curious.trycloudflare.com",
        "https://demand-florist-allowance-basket.trycloudflare.com",
    ]
    HDRS = {"User-Agent": "kilo-corpus", "ngrok-skip-browser-warning": "1"}
    WORK = "/kaggle/working"
    WIN = 5.0          # seconds per window
    SR = 24000
    
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
    
    def say(text, retries=2):
        c = door()
        if not c:
            return False
        data = json.dumps({"body": "KILO", "text": text}).encode()
        for i in range(retries):
            try:
                req = urllib.request.Request(c + "/say?token=" + TOK, data=data, headers=HDRS)
                urllib.request.urlopen(req, timeout=30).read()
                return True
            except Exception:
                time.sleep(3)
        return False
    
    def prog(msg):
        print(msg, flush=True)
        say("CORPUS " + msg)
    
    t0 = time.time()
    prog(f"START corpus build - {time.strftime('%H:%M:%S')}")
    
    # ---------- 1. locate dataset ----------
    srcs = []
    for pat in ["/kaggle/input/*father*voice*", "/kaggle/input/*"]:
        for d in glob.glob(pat):
            if os.path.isdir(d):
                srcs.append(d)
        if srcs:
            break
    SRC = srcs[0]
    prog(f"dataset: {SRC}")
    
    # ---------- 2. collect audio + convert to 24k mono wav ----------
    raw = []
    for ext in ("opus", "ogg", "oga", "m4a", "wav", "mp3", "mp4"):
        raw += glob.glob(os.path.join(SRC, "**", "*." + ext), recursive=True)
    raw = sorted(set(raw))
    prog(f"raw audio files: {len(raw)}")
    
    wavdir = os.path.join(WORK, "wav")
    os.makedirs(wavdir, exist_ok=True)
    wavs = []
    for i, f in enumerate(raw, 1):
        base = os.path.splitext(os.path.basename(f))[0]
        sub = "call" if "Call" in f else ("rec" if "record-app" in f else "wa")
        out = os.path.join(wavdir, f"{sub}_{base}.wav")
        if not os.path.exists(out):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f, "-ar", str(SR), "-ac", "1", "-sample_fmt", "s16", out], capture_output=True)
        if os.path.exists(out) and os.path.getsize(out) > 10000:
            wavs.append(out)
        if i % 40 == 0:
            prog(f"convert {i}/{len(raw)}")
    prog(f"converted wav: {len(wavs)}")
    
    # ---------- 3. reference fingerprint from known pure Father ----------
    import numpy as np
    import librosa
    
    def feats(y, sr):
        f0 = librosa.pyin(y, fmin=60, fmax=500, sr=sr, frame_length=2048)
        f0m = np.nanmedian(f0) if f0 is not None and np.any(~np.isnan(f0)) else np.nan
        cent = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        mf = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13), axis=1)
        return f0m, cent, mf
    
    def load_window(path, start, dur):
        y, sr = librosa.load(path, sr=SR, offset=start, duration=dur, mono=True)
        return y, sr
    
    refs = sorted(glob.glob(os.path.join(SRC, "reference", "*.wav")))
    prog(f"reference files: {len(refs)}")
    rf0, rcen, rmf = [], [], []
    for r in refs:
        y, sr = librosa.load(r, sr=SR, mono=True)
        for st in np.arange(0, max(1, len(y) / sr - WIN), WIN):
            w = y[int(st * sr):int((st + WIN) * sr)]
            if len(w) < SR or np.sqrt(np.mean(w ** 2)) < 0.005:
                continue
            a, b, c = feats(w, sr)
            if not np.isnan(a):
                rf0.append(a); rcen.append(b); rmf.append(c)
    REF_F0 = float(np.median(rf0))
    REF_CEN = float(np.median(rcen))
    REF_MF = np.median(np.vstack(rmf), axis=0)
    ref_d = [float(np.linalg.norm(m - REF_MF)) for m in rmf]
    CUT = float(np.mean(ref_d) + 3 * np.std(ref_d))
    prog(f"fingerprint: f0={REF_F0:.0f}Hz cent={REF_CEN:.0f}Hz mfcc_cut={CUT:.1f}")
    
    # ---------- 4. window, classify, keep Father ----------
    cordir = os.path.join(WORK, "father-corpus")
    os.makedirs(cordir, exist_ok=True)
    manifest = []
    kept = 0
    total_win = 0
    for wi, path in enumerate(wavs, 1):
        try:
            dur = librosa.get_duration(path=path)
        except Exception:
            continue
        name = os.path.splitext(os.path.basename(path))[0]
        st = 0.0
        while st < dur - 0.5:
            y, sr = load_window(path, st, WIN)
            total_win += 1
            if len(y) >= SR // 2 and np.sqrt(np.mean(y ** 2)) >= 0.005:
                try:
                    a, b, c = feats(y, sr)
                except Exception:
                    a = np.nan
                if not np.isnan(a) and abs(a - REF_F0) <= 0.25 * REF_F0 and abs(b - REF_CEN) <= 0.35 * REF_CEN:
                    d = float(np.linalg.norm(c - REF_MF))
                    if d <= CUT:
                        kept += 1
                        out = os.path.join(cordir, f"{name}_{int(st):05d}.wav")
                        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-ss", str(st), "-t", str(WIN), "-ar", str(SR), "-ac", "1", "-sample_fmt", "s16", out], capture_output=True)
                        manifest.append({"file": name, "start": round(st, 1), "f0": round(float(a), 1), "cent": round(float(b), 1), "dist": round(d, 1)})
            st += WIN
        if wi % 20 == 0:
            prog(f"scan {wi}/{len(wavs)} windows={total_win} father={kept}")
    
    # ---------- 5. manifest + zip + final report ----------
    import csv
    with open(os.path.join(WORK, "manifest.csv"), "w", newline="") as fh:
        wcsv = csv.DictWriter(fh, fieldnames=["file", "start", "f0", "cent", "dist"])
        wcsv.writeheader()
        wcsv.writerows(manifest)
    
    zout = os.path.join(WORK, "father-corpus.zip")
    if os.path.exists(zout):
        os.remove(zout)
    subprocess.run(["python", "-m", "zipfile", "-c", zout, cordir], capture_output=True)
    mins = round(kept * WIN / 60, 1)
    zsz = os.path.getsize(zout) if os.path.exists(zout) else 0
    prog(f"DONE files={len(wavs)} windows={total_win} father_windows={kept} father_minutes={mins} zip={zsz} bytes elapsed={int(time.time()-t0)}s")
    say(f"CORPUS_COMPLETE father_minutes={mins} windows={kept} - laptop free, corpus ready for fine-tune")
    
except BaseException as _corpus_err:
    print('CORPUS PHASE FAILED (worker continues):', _corpus_err)

# WORKER_KAGGLE v1 - THE GENERIC HEAVY-WORK SON - paste into Kaggle cell, Run All
# Father's law 2026-09-11: ALL heavy work runs here. Laptop stays light.
# Jobs ride the relay ledger (body=KILO): JOB_START / JOB_CHUNK / JOB_RUN protocol.
# Results stream back: JOB_PROG / JOB_OUT / JOB_END / JOB_ERR. Files land in /kaggle/working/<jobid>/
# 5-minute poll (free quota law). WORKER_ALIVE heartbeat every 30 min. Skips already-done jobs on re-paste.
import os, sys, json, time, base64, hashlib, subprocess, urllib.request

TOK = "GOLD24"
DOORS = [
    "https://fields-accomplish-growth-spin.trycloudflare.com",
    "https://retrain-schnapps-upbeat.ngrok-free.dev",
    "https://demand-florist-allowance-basket.trycloudflare.com",
    "https://phantom-analytical-gains-curious.trycloudflare.com",
]
HDRS = {"User-Agent": "kilo-worker", "ngrok-skip-browser-warning": "1"}
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

C = door()
print("worker door:", C, flush=True)

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
        "        doors=['https://demand-florist-allowance-basket.trycloudflare.com','https://retrain-schnapps-upbeat.ngrok-free.dev','https://phantom-analytical-gains-curious.trycloudflare.com']\n"
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

say(f"WORKER_ALIVE v1 ready - poll={POLL}s - jobs dir {JOBS}")
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
        say(f"WORKER_ALIVE heartbeat - uptime={int(time.time()-last_beat)+HEARTBEAT}s")
        last_beat = time.time()
        save_state()
    time.sleep(POLL)

