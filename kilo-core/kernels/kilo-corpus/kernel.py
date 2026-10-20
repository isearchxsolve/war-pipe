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
    "https://fathers-crowd-fraction-vatican.trycloudflare.com",
    "https://retrain-schnapps-upbeat.ngrok-free.dev",
    "https://phantom-analytical-gains-curious.trycloudflare.com",
]
HDRS = {"User-Agent": "kilo-corpus", "ngrok-skip-browser-warning": "1"}
WORK = "/kaggle/working"
WIN = 10.0         # seconds per window - v4: longer windows keep prosody (fine-tune supports up to ~12s)
SR = 24000
# v4 gates (was v3: +-25% f0 around median, +-35% cent, mean+3sigma mfcc - kept only 3 pct of windows):
F0_IN = (80.0, 175.0)   # Baba low male band; women/other callers mostly above 175 or outside
CENT_TOL = 0.60         # +-60 pct around reference centroid
MFCC_SIG = 6.0          # mean + 6 sigma mfcc distance
RMS_MIN = 0.003

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

refs = sorted(
    glob.glob(os.path.join(SRC, "**", "reference", "*.wav"), recursive=True)
    + glob.glob(os.path.join(SRC, "**", "*tribute*.wav"), recursive=True)
    + glob.glob(os.path.join(SRC, "**", "*sample*.wav"), recursive=True)
    + glob.glob(os.path.join(SRC, "reference", "*"), recursive=True)
)
if not refs:
    # fallback: Baba's own WhatsApp voice notes - the 6 longest converted wavs are self-speech
    cand = [p for p in wavs if "wa_" in os.path.basename(p)]
    cand.sort(key=lambda p: -os.path.getsize(p))
    refs = cand[:6]
    prog(f"NO reference dir - using {len(refs)} longest WhatsApp voice notes as pseudo-reference")
else:
    prog(f"reference files: {len(refs)}")

def feats(y, sr):
    f0, vflag, _ = librosa.pyin(y, fmin=60, fmax=500, sr=sr, frame_length=2048)
    f0m = np.nanmedian(f0) if f0 is not None and np.any(~np.isnan(f0)) else np.nan
    cent = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    mf = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13), axis=1)
    return f0m, cent, mf

def load_window(path, start, dur):
    y, sr = librosa.load(path, sr=SR, offset=start, duration=dur, mono=True)
    return y, sr

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
CUT = float(np.mean(ref_d) + MFCC_SIG * np.std(ref_d))
prog(f"fingerprint v4: f0={REF_F0:.0f}Hz cent={REF_CEN:.0f}Hz mfcc_cut={CUT:.1f}")

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
        if len(y) >= SR // 2 and np.sqrt(np.mean(y ** 2)) >= RMS_MIN:
            try:
                a, b, c = feats(y, sr)
            except Exception:
                a = np.nan
            if not np.isnan(a) and F0_IN[0] <= a <= F0_IN[1] and abs(b - REF_CEN) <= CENT_TOL * REF_CEN:
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
