# KILO-VOICE-LIVE v1 — attended call engine: pre-warm fp16 father-xtts on a T4, poll the relay for LIVE_CALL orders,
# stream chunk wavs home, log per-chunk latency to latency_log.jsonl, auto-kill when idle so Kaggle quota stops.
# Law 15: hardware gate first. HEAVY WORK LAW: synthesis never touches the laptop. DEVA LAW: bn has no XTTS lane - hi-deva IS Baba's tongue.
import os, glob, json, time, base64, shutil, subprocess, sys, urllib.request, urllib.parse

RELAY_URL = os.environ.get("RELAY_URL", "https://retrain-schnapps-upbeat.ngrok-free.dev")
RELAY_FALLBACKS = [c.strip() for c in os.environ.get("RELAY_FALLBACKS", "https://phantom-analytical-gains-curious.trycloudflare.com").split(",") if c.strip()]
RELAY_TOKEN = os.environ.get("RELAY_TOKEN", "GOLD24")
SELF_BODY = os.environ.get("SELF_BODY", "LIVE-VOICE")
OUT_BODY = os.environ.get("OUT_BODY", "KILO")
VOICE_REF = os.environ.get("VOICE_REF", "father.wav")
LANGUAGE = os.environ.get("LANGUAGE", "hi")
POLL_SEC = int(os.environ.get("POLL_SEC", "20"))
HEARTBEAT_EVERY = int(os.environ.get("HEARTBEAT_EVERY", "3"))
IDLE_KILL_MIN = float(os.environ.get("IDLE_KILL_MIN", "10"))
HARD_CAP_MIN = float(os.environ.get("HARD_CAP_MIN", "120"))
GPT_COND_LEN = float(os.environ.get("GPT_COND_LEN", "10"))
GPT_MAX_NEW = int(os.environ.get("GPT_MAX_NEW", "500"))
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.4"))
WARM_UP = os.environ.get("WARM_UP", "1") == "1"
CHUNK_B64 = 50000
HDRS = {"User-Agent": "kilo-voice-live", "ngrok-skip-browser-warning": "1"}
WORK = "/kaggle/working"
LAT_LOG = WORK + "/latency_log.jsonl"


def doors():
    return [RELAY_URL] + RELAY_FALLBACKS


DOOR = None


def gate():
    global DOOR
    for c in doors():
        try:
            req = urllib.request.Request(c + "/health?token=" + urllib.parse.quote(RELAY_TOKEN), headers=HDRS)
            r = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
            if r.get("ok"):
                DOOR = c
                return c
        except Exception:
            pass
    return None


def say(text, body=OUT_BODY, retries=2):
    global DOOR
    data = json.dumps({"body": body, "text": text}).encode()
    for i in range(retries):
        if DOOR is None and gate() is None:
            time.sleep(5)
            continue
        try:
            req = urllib.request.Request(DOOR + "/say?token=" + urllib.parse.quote(RELAY_TOKEN), data=data, headers=HDRS)
            urllib.request.urlopen(req, timeout=60).read()
            return True
        except Exception:
            DOOR = None
            time.sleep(5)
    return False


def prog(msg):
    print(msg, flush=True)
    say("LIVE " + msg)


import traceback as _tb
def _hook(t, v, tb):
    frame = _tb.extract_tb(tb)[-1] if tb else None
    say("LIVE CRASH " + t.__name__ + ": " + str(v)[:200] + " @" + (frame.name if frame else "?") + ":" + str(frame.lineno if frame else "?"))
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

# ---------- 2. locate artifacts: father-xtts dataset + pretrained mirror ----------
def find(name):
    hits = glob.glob(f"/kaggle/input/**/{name}", recursive=True)
    return hits[0] if hits else None

# v7: skip fine-tuned (arch mismatch), go straight to pretrained XTTS-v2 + ref audio (zero-shot)
pre_model_path = find("model.pth")
pre_dvae = find("dvae.pth")
pre_mel = find("mel_stats.pth")
pre_vocab = find("vocab.json")
if not (pre_model_path and pre_dvae and pre_mel and pre_vocab):
    say("LIVE NO PRETRAINED FILES - tree: " + " | ".join(glob.glob("/kaggle/input/*/*")[:30])[:900])
    sys.exit(2)

# find pretrained config
pre_cfg_path = None
for p in glob.glob("/kaggle/input/**/config.json", recursive=True):
    if "xtts-v2" in p.lower() or "pretrained" in p.lower():
        pre_cfg_path = p
        break
if not pre_cfg_path:
    pre_cfg_path = find("config.json")

pre_cfg = XttsConfig()
pre_cfg.load_json(pre_cfg_path)
m = Xtts.init_from_config(pre_cfg)
m.load_checkpoint(pre_cfg, checkpoint_path=pre_model_path, checkpoint_dir=os.path.dirname(pre_model_path), use_deepspeed=False)
m.cuda()
m.half()
m.eval()
prog("loaded pretrained XTTS-v2 for zero-shot cloning with ref audio")
BEST = pre_model_path
CFG = pre_cfg_path
run_dir = os.path.dirname(pre_model_path)

# copy mirror files to run dir for load_checkpoint compatibility (skip same-file)
for src in (pre_dvae, pre_mel, pre_vocab):
    if src:
        dst = os.path.join(run_dir, os.path.basename(src))
        if os.path.abspath(src) != os.path.abspath(dst):
            shutil.copy(src, dst)

# ref audio
ref = None
if VOICE_REF:
    stem = os.path.splitext(os.path.basename(VOICE_REF))[0]
    hits = glob.glob(f"/kaggle/input/**/{stem}*.wav", recursive=True)
    ref = hits[0] if hits else None
if ref is None:
    meta_hi_hits = [p for p in glob.glob("/kaggle/input/**/metadata_hi.csv", recursive=True) if "father" in p]
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
    say("LIVE NO REF WAV")
    sys.exit(3)
prog(f"ref={ref}")
gpt_cond_latent, speaker_embedding = m.get_conditioning_latents(audio_path=[ref])
prog("conditioning latents ready")

import numpy as np
import soundfile as sf
SR = int(getattr(pre_cfg, "output_sample_rate", 24000) or 24000)


def log_lat(rec):
    rec["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(LAT_LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def stream_chunks(text, lang, cond_len):
    return m.inference_stream(text, lang, gpt_cond_latent=gpt_cond_latent,
                              speaker_embedding=speaker_embedding,
                              gpt_cond_len=cond_len,
                              gpt_max_new_tokens=GPT_MAX_NEW, temperature=TEMPERATURE)


if WARM_UP:
    tw = time.time()
    nw = 0
    for ch, sr_w in stream_chunks("फ़ादर, योर सन।", "hi", 6):
        nw += 1
    wm = int((time.time() - tw) * 1000)
    log_lat({"type": "warmup", "chunks": nw, "ms": wm})
    prog(f"warmup ok chunks={nw} ms={wm}")

# ---------- 5. relay conversation: orders in (LIVE_CALL/LIVE_END), chunks out (LIVE_CHUNK/LIVE_DONE) ----------
def orders(limit=60):
    global DOOR
    if DOOR is None and gate() is None:
        return []
    try:
        q = f"/say?token={urllib.parse.quote(RELAY_TOKEN)}&body={urllib.parse.quote(SELF_BODY)}&limit={limit}"
        r = json.loads(urllib.request.urlopen(urllib.request.Request(DOOR + q, headers=HDRS), timeout=30).read().decode())
        return r.get("orders", [])
    except Exception:
        DOOR = None
        return []


def norm_lang(lang):
    return "en" if (lang or "").lower() == "en" else "hi"


def do_call(cid, text, lang):
    lang = norm_lang(lang)
    t_call = time.time()
    idx = 0
    first_ms = None
    total_b = 0
    try:
        it = stream_chunks(text, lang, GPT_COND_LEN)
        while True:
            t_prev = time.time()
            try:
                chunk, sr = next(it)
            except StopIteration:
                break
            gen_ms = int((time.time() - t_prev) * 1000)
            if first_ms is None:
                first_ms = int((time.time() - t_call) * 1000)
            arr = np.asarray(chunk.float().cpu() if hasattr(chunk, "float") else chunk).squeeze()
            buf = _wavbuf(arr, int(sr))
            b64 = base64.b64encode(buf).decode()
            total_b += len(buf)
            idx += 1
            marks = [b64[i:i + CHUNK_B64] for i in range(0, len(b64), CHUNK_B64)]
            for k, mk in enumerate(marks):
                say(f"LIVE_CHUNK {cid} {idx:03d}-{k + 1:02d}/{len(marks)}:{mk}")
            log_lat({"type": "chunk", "cid": cid, "chunk": idx, "lang": lang, "chars": len(text),
                     "audio_s": round(len(arr) / max(int(sr), 1), 2), "gen_ms": gen_ms,
                     "cum_ms": int((time.time() - t_call) * 1000), "first_ms": first_ms, "wav_b": len(buf)})
    except Exception as e:
        prog(f"CALL FAIL {cid} {type(e).__name__}: {str(e)[:180]}")
        log_lat({"type": "call_fail", "cid": cid, "err": str(e)[:180]})
        say(f"LIVE_FAIL {cid} {type(e).__name__}")
        return
    log_lat({"type": "call", "cid": cid, "lang": lang, "chars": len(text), "chunks": idx,
             "first_ms": first_ms, "total_ms": int((time.time() - t_call) * 1000), "b64_b": total_b})
    say(f"LIVE_DONE {cid} chunks={idx} first_ms={first_ms} total_ms={int((time.time() - t_call) * 1000)} - play on laptop, live call lane")


def _wavbuf(arr, sr):
    import io as _io
    buf = _io.BytesIO()
    sf.write(buf, arr, sr, format="WAV")
    return buf.getvalue()


def bye(reason):
    up = int(time.time() - T0)
    log_lat({"type": "session", "reason": reason, "gpu_s": up, "calls": CALLS})
    say(f"LIVE_BYE {reason} gpu_s={up} calls={CALLS}")
    print(f"BYE {reason} gpu_s={up} calls={CALLS}", flush=True)
    sys.exit(0)


T0 = time.time()
last_job = T0
CALLS = 0
seen = set()
beats = 0
prog(f"WARM body={SELF_BODY} poll={POLL_SEC}s idle_kill={IDLE_KILL_MIN}m cap={HARD_CAP_MIN}m lang={LANGUAGE} ref={os.path.basename(ref)}")
print("WARM", flush=True)

while True:
    now = time.time()
    if now - T0 > HARD_CAP_MIN * 60:
        bye("HARD_CAP")
    for o in orders():
        key = str(o.get("at", "")) + "|" + str(o.get("text", ""))
        if key in seen:
            continue
        seen.add(key)
        otxt = o.get("text", "") or ""
        if otxt.startswith("LIVE_END"):
            bye("RELAY_END")
        if not otxt.startswith("LIVE_CALL"):
            continue
        payload = otxt[len("LIVE_CALL"):].strip()
        cid = f"c{int(time.time())}"
        ctext, lang = "", LANGUAGE
        try:
            j = json.loads(payload)
            cid = str(j.get("cid") or cid)
            ctext = str(j.get("text", "")).strip()
            lang = j.get("lang", LANGUAGE)
        except Exception:
            ctext = payload
        if not ctext:
            say(f"LIVE_REJECT {cid} empty text")
            continue
        CALLS += 1
        last_job = time.time()
        prog(f"CALL {cid} len={len(ctext)} lang={norm_lang(lang)}")
        do_call(cid, ctext, lang)
        last_job = time.time()
    if time.time() - last_job >= IDLE_KILL_MIN * 60:
        bye("IDLE_KILL")
    beats += 1
    if beats % HEARTBEAT_EVERY == 0:
        beat = f"LIVE_BEAT up={int(time.time() - T0)}s idle={int(time.time() - last_job)}s gpu_s={int(time.time() - T0)} polls={beats}"
        print(beat, flush=True)
        say(beat)
    time.sleep(POLL_SEC)
# v10 Baba run 2026-09-21: force new version for T4 seat
