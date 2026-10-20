# KILO-XTTS-INFER v1 — load v15 best_model.pth (kernel-chained input), deva ear-test, stream home.
# Law 15: hardware gate first. Law 11/12: two entities, deva text, chunked pure bytes home.
import os, glob, json, time, base64, shutil, subprocess, sys, urllib.request

TOK = "GOLD24"
DOOR = "https://fathers-crowd-fraction-vatican.trycloudflare.com"
HDRS = {"User-Agent": "kilo-infer", "ngrok-skip-browser-warning": "1"}
WORK = "/kaggle/working"


def say(text, body="KILO", retries=2):
    data = json.dumps({"body": body, "text": text}).encode()
    for i in range(retries):
        try:
            req = urllib.request.Request(DOOR + "/say?token=" + TOK, data=data, headers=HDRS)
            urllib.request.urlopen(req, timeout=60).read()
            return True
        except Exception:
            time.sleep(5)
    return False


def prog(msg):
    print(msg, flush=True)
    say("INFER " + msg)


import traceback as _tb
def _hook(t, v, tb):
    frame = _tb.extract_tb(tb)[-1] if tb else None
    say("INFER CRASH " + t.__name__ + ": " + str(v)[:200] + " @" + (frame.name if frame else "?") + ":" + str(frame.lineno if frame else "?"))
sys.excepthook = _hook

# ---------- 0. HARDWARE GATE (law 15) ----------
smi = subprocess.run(["nvidia-smi", "--query-gpu=index,name,memory.total", "--format=csv,noheader"],
                     capture_output=True, text=True).stdout.strip()
prog("nvidia-smi: " + smi.replace("\n", " | "))
import torch as _gate
_names = [_gate.cuda.get_device_name(i) for i in range(_gate.cuda.device_count())]
assert _gate.cuda.device_count() >= 1 and all("T4" in n.upper() for n in _names), \
    f"HARDWARE GATE FAIL: expected T4, got {_names}"
prog(f"GATE PASS: {_names}")

# ---------- 1. coqui ----------
def pip(*args):
    return subprocess.call([sys.executable, "-m", "pip", "install", "-q"] + list(args))

try:
    import TTS  # noqa
    prog("TTS importable")
except Exception:
    if pip("coqui-tts") != 0:
        pip("--ignore-requires-python", "coqui-tts")

from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

# ---------- 2. locate artifacts: tune-kernel output (chained) + pretrained mirror ----------
def find(name):
    hits = glob.glob(f"/kaggle/input/**/{name}", recursive=True)
    return hits[0] if hits else None

BEST = find("father_last_fp16.pth") or find("father_last.pth") or find("best_model.pth")
CFG = None
for p in glob.glob("/kaggle/input/**/config.json", recursive=True):
    if "father-xtts" in p:
        CFG = p
        break
if CFG is None:
    CFG = find("config.json")
if not BEST or not CFG:
    say("INFER NO ARTIFACT - tree: " + " | ".join(glob.glob("/kaggle/input/*/*")[:30])[:900])
    sys.exit(2)
DV = find("dvae.pth")
ME = find("mel_stats.pth")
VO = find("vocab.json")
if not (DV and ME and VO):
    say("INFER MIRROR FILES MISSING dvae/mel/vocab")
    sys.exit(2)
# dataset mounts are READ-ONLY: assemble a writable run dir for load_checkpoint
RUN = WORK + "/run"
os.makedirs(RUN, exist_ok=True)
shutil.copy(BEST, RUN + "/father_last.pth")
shutil.copy(CFG, RUN + "/config.json")
for src in (DV, ME, VO):
    shutil.copy(src, os.path.join(RUN, os.path.basename(src)))
BEST = RUN + "/father_last.pth"
CFG = RUN + "/config.json"
run_dir = RUN
prog(f"best={BEST} cfg={CFG}")

# ---------- 3. reference wav: first clean hi row of father-corpus ----------
meta_hi_hits = [p for p in glob.glob("/kaggle/input/**/metadata_hi.csv", recursive=True) if "father" in p]
ref = None
if meta_hi_hits:
    first = None
    for line in open(meta_hi_hits[0], encoding="utf-8"):
        if "|" in line:
            first = os.path.basename(line.split("|", 1)[0])
            break
    if first:
        stem = os.path.splitext(first)[0]
        hits = glob.glob(f"/kaggle/input/**/{stem}*.wav", recursive=True)
        ref = hits[0] if hits else None
if ref is None:
    hits = glob.glob("/kaggle/input/**/windows/*.wav", recursive=True)
    ref = hits[0] if hits else None
if ref is None:
    say("INFER NO REF WAV")
    sys.exit(3)
prog(f"ref={ref}")

# ---------- 4. load + synthesize (correct API: Xtts.synthesize) ----------
cfg = XttsConfig()
cfg.load_json(CFG)
m = Xtts.init_from_config(cfg)
m.load_checkpoint(cfg, checkpoint_path=BEST, checkpoint_dir=run_dir, use_deepspeed=False)
m.cuda()
m.half()
m.eval()
prog("model loaded")

deva_text = "फ़ादर, योर सन हियर्स यू। आई एम प्राउड टू बी योर सन। आई लव यू, फ़ादर।"  # DEVA LAW
t0 = time.time()
wav = None
attempts = [
    lambda: m.synthesize(text=deva_text, config=cfg, speaker_wav=ref, language="hi", gpt_cond_len=10),
    lambda: m.synthesize(deva_text, cfg, speaker_wav=ref, language="hi", gpt_cond_len=6),
]
for att in attempts:
    try:
        r = att()
        wav = r["wav"] if isinstance(r, dict) else r
        break
    except Exception as ie:
        prog(f"SYN attempt fail {type(ie).__name__} {str(ie)[:160]}")
if wav is None:
    say("INFER FAILED all synthesize attempts")
    sys.exit(4)

import numpy as np
arr = np.asarray(wav).squeeze()
out = WORK + "/father_deva_test.wav"
import soundfile as sf
sr = int(getattr(cfg, "output_sample_rate", 24000) or 24000)
sf.write(out, arr, sr)
sz = os.path.getsize(out)
prog(f"wav written {sz}B in {int(time.time()-t0)}s sr={sr}")

# ---------- 5. stream home (two entities law) ----------
b64 = base64.b64encode(open(out, "rb").read()).decode()
chunks = [b64[i:i+50000] for i in range(0, len(b64), 50000)]
for idx, ch in enumerate(chunks):
    say(f"XTTS_CHUNK {idx+1:02d}/{len(chunks)}:{ch}")
    time.sleep(0.2)
say(f"XTTS_DONE {len(b64)} v15 fine-tuned baba voice deva test - play on laptop, ear-check vs tribute")
prog(f"DONE chunks={len(chunks)} total={int(time.time()-t0)}s")
