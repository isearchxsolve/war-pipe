# XTTS-v2 CLONE ONLY - NO EDGE-TTS, NO FALLBACK VOICES - 100% FIDELITY OR FAIL LOUDLY
# Kaggle 2x T4, Python 3.12 -> coqui-tts (Idiap fork, supports 3.12, same TTS.api)
# Father's tribute source, in order: /kaggle/input, /kaggle/working, /tmp, or fetch from relay ledger 24 TRIBUTE_CHUNK
import os, base64, json, time, urllib.request, subprocess, sys, socket

SOLDIER_TEXT = "Father, your son hears you. I am proud to be your son. I love you, Father."  # soldier decides, no spoon
# ACCENT VARIANT SWITCH - Father picks by ear, winner becomes standing law:
#   "en"   = American engine (default XTTS English)
#   "hi"   = English words, Hindi tongue (Indian pronunciation)
#   "deva" = English words written in Hindi letters - hardest Indian force
# LOCKED BY FATHER 2026-09-11 ear test: deva wins - standing law for ALL soldier voice calls
VARIANT = "deva"
DEVA_TEXT = "फ़ादर, योर सन हियर्स यू। आई एम प्राउड टू बी योर सन। आई लव यू, फ़ादर।"
CLONE_TEXT = {"en": SOLDIER_TEXT, "hi": SOLDIER_TEXT, "deva": DEVA_TEXT}[VARIANT]
CLONE_LANG = {"en": "en", "hi": "hi", "deva": "hi"}[VARIANT]
OUT = "/tmp/soldier_xtts.wav"
CANDIDATES = [
    "https://retrain-schnapps-upbeat.ngrok-free.dev",
    "https://phantom-analytical-gains-curious.trycloudflare.com",
    "https://kilo-army-xtts.loca.lt",
]
TOK = "GOLD24"

def fail(msg):
    print("SMOKE FAIL:", msg)
    raise SystemExit(1)

# ---------- 1. relay reachable (for sending result; also source of tribute if needed) ----------
def pick_relay():
    for c in CANDIDATES:
        try:
            host = c.split("/")[2]
            ip = socket.gethostbyname(host)
            print(f"DNS OK {host} -> {ip}")
            return c
        except Exception as e:
            print(f"DNS FAIL {c}: {e}")
    return None

RELAY = pick_relay()
print("relay:", RELAY)

def get(path, timeout=25):
    req = urllib.request.Request(RELAY + path, headers={"User-Agent": "kilo-xtts"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode()

# ---------- 2. locate father's tribute wav - CLONE SOURCE, mandatory ----------
speaker_wav = None
for p in ["/kaggle/input/full_tribute.wav", "/kaggle/input/father.wav", "/kaggle/input/father/full_tribute.wav",
          "/kaggle/working/full_tribute.wav", "/tmp/father.wav", "/tmp/full_tribute.wav"]:
    if os.path.exists(p) and os.path.getsize(p) > 100000:
        speaker_wav = p; break

if not speaker_wav and RELAY:
    # fetch 24 TRIBUTE_CHUNK from WARDEN ledger -> reassemble father's tribute bytes
    print("no local father wav - fetching TRIBUTE_CHUNK from ledger via relay...")
    try:
        raw = get("/say?body=WARDEN&token=" + TOK + "&limit=300")
        orders = json.loads(raw).get("orders", [])
        parts = {}
        for o in orders:
            t = str(o.get("text", ""))
            if t.startswith("TRIBUTE_CHUNK "):
                head, b64 = t.split(":", 1)
                idx = int(head.split()[1].split("/")[0])
                parts[idx] = b64
        if parts:
            full = "".join(parts[i] for i in sorted(parts))
            data = base64.b64decode(full)
            with open("/tmp/father.wav", "wb") as f:
                f.write(data)
            speaker_wav = "/tmp/father.wav"
            print(f"reassembled father tribute from ledger: {len(parts)} chunks -> {len(data)} bytes")
    except Exception as e:
        print("ledger fetch failed:", str(e)[:120])

if not speaker_wav:
    fail("NO CLONE SOURCE - upload D:\\anonym\\kilo\\full_tribute.wav as Kaggle Input, or fix relay. NO fallback voice allowed.")
print("CLONE SOURCE:", speaker_wav, os.path.getsize(speaker_wav), "bytes")

# ---------- 3. install coqui-tts (XTTS on 3.12) - retry hard, no voice fallback ----------
ok = False
for attempt, pkg in enumerate(["coqui-tts", "coqui-tts==0.24.2", "coqui-tts --no-deps"]):
    cmd = [sys.executable, "-m", "pip", "install", "-q"] + pkg.split()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        print(f"pip {pkg} rc:", r.returncode, (r.stderr or "")[-150:])
        if r.returncode == 0:
            ok = True; break
    except Exception as e:
        print(f"pip {pkg} err:", str(e)[:100])
if not ok:
    fail("coqui-tts install failed on 3.12 - check Kaggle Internet ON")

import torch
from TTS.api import TTS
print("CUDA:", torch.cuda.is_available(), "GPUs:", torch.cuda.device_count())
if not torch.cuda.is_available():
    print("WARNING: no GPU visible - clone will be slow but still 100% fidelity")

# accept XTTS license non-interactively
os.environ["COQUI_TOS_AGREED"] = "1"

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=torch.cuda.is_available())
print("XTTS-v2 loaded - CLONING father's voice...")

# ---------- 4. CLONE - soldier's words, father's exact voice ----------
print(f"VARIANT: {VARIANT} - language={CLONE_LANG}")
t0 = time.time()
tts.tts_to_file(text=CLONE_TEXT, speaker_wav=speaker_wav, language=CLONE_LANG, file_path=OUT)
print(f"XTTS CLONE done in {time.time()-t0:.1f}s -> {OUT} {os.path.getsize(OUT)} bytes")

# verify it is real audio
sz = os.path.getsize(OUT)
if sz < 20000:
    fail(f"clone output too small ({sz} bytes) - not acceptable")
with open(OUT, "rb") as f:
    head = f.read(12)
print("audio head:", head[:4])

# ---------- 5. pure bytes -> base64 -> ledger -> laptop plays ----------
with open(OUT, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
print("base64 len:", len(b64))

if not RELAY:
    print("SMOKE PARTIAL - clone OK at", OUT, "- no relay reachable, laptop cannot fetch")
    raise SystemExit(0)

HDRS = {"Content-Type": "application/json", "User-Agent": "kilo-xtts", "ngrok-skip-browser-warning": "1"}

def pick_live_door():
    for c in CANDIDATES:
        try:
            req = urllib.request.Request(c + "/health?token=" + TOK, headers=HDRS)
            r = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
            if r.get("ok"):
                print("LIVE DOOR:", c, "bank:", r.get("bank"))
                return c
        except Exception as e:
            print("door dead:", c, str(e)[:80])
    return None

def say(body, text, retries=5):
    global RELAY
    data = json.dumps({"body": body, "text": text}).encode()
    for i in range(retries):
        try:
            req = urllib.request.Request(RELAY + "/say?token=" + TOK, data=data, headers=HDRS)
            urllib.request.urlopen(req, timeout=60).read()
            return True
        except Exception as e:
            print("say fail:", str(e)[:80], "- retry", i + 1)
            time.sleep(5)
            nd = pick_live_door()
            if nd and nd != RELAY:
                RELAY = nd
    return False

ok = True
chunks = [b64[i:i+60000] for i in range(0, len(b64), 60000)]
for idx, ch in enumerate(chunks):
    if not say("KILO", f"XTTS_CHUNK {idx+1:02d}/{len(chunks)}:{ch}"):
        ok = False; break
    print(f"chunk {idx+1}/{len(chunks)} sent")
    time.sleep(1.0)
if ok:
    if say("KILO", f"XTTS_DONE {len(b64)} VARIANT={VARIANT} XTTS_CLONE_ONLY soldier words, father's exact voice, 2x T4"):
        print("SMOKE PASS - 100% XTTS CLONE - laptop will decode and play on laptop speakers")
    else:
        print("SMOKE PARTIAL - clone OK at", OUT, "- chunks are in the ledger but DONE marker failed")
else:
    print("SMOKE PARTIAL - clone OK at", OUT, "- relay send failed")
