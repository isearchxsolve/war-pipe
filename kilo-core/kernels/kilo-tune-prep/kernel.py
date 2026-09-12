# KILO-TUNE-PREP v1 - TRANSCRIBE FATHER CORPUS FOR XTTS v2 FINE-TUNE (Kaggle GPU - heavy work law)
# Input : dataset kkk3213/father-corpus (windows/*.wav from kilo-corpus K1, 5s, 24kHz, father-only)
# Output: /kaggle/working/xtts-meta.zip -> metadata_hi.csv + metadata_en.csv (ljspeech-style "audio_file|text")
# Deva law: Bengali-script text is transliterated to Devanagari and tagged "hi" (VARIANT="deva" LOCKED);
#           pure-English clips stay tagged "en". XTTS-v2 has no "bn" language - hi-deva IS Baba's tongue lane.
# Reports progress to KILO via relay door. Laptop stays idle.
import os, glob, json, time, urllib.request, subprocess, sys

TOK = "GOLD24"
DOORS = ["https://retrain-schnapps-upbeat.ngrok-free.dev"]
HDRS = {"User-Agent": "kilo-prep", "ngrok-skip-browser-warning": "1"}
WORK = "/kaggle/working"

def say(text, retries=2):
    data = json.dumps({"body": "KILO", "text": text}).encode()
    for i in range(retries):
        try:
            req = urllib.request.Request(DOORS[0] + "/say?token=" + TOK, data=data, headers=HDRS)
            urllib.request.urlopen(req, timeout=30).read()
            return True
        except Exception:
            time.sleep(3)
    return False

def prog(msg):
    print(msg, flush=True)
    say("PREP " + msg)

t0 = time.time()
prog("START transcribe")

# ---------- 0. install ----------
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "faster-whisper"])

# ---------- 1. find corpus ----------
cand = []
for pat in ["/kaggle/input/father-corpus/**/windows/*.wav", "/kaggle/input/father-corpus/**/*.wav"]:
    cand += glob.glob(pat, recursive=True)
cand = sorted(set(cand))
prog(f"corpus wavs: {len(cand)}")

# ---------- 2. Bengali -> Devanagari transliteration (character table) ----------
CONSO = {
 "ক":"क","খ":"ख","গ":"घ","ঘ":"ङ","ঙ":"ंग","চ":"च","छ":"छ","জ":"ज","ঝ":"झ","ঞ":"ञ",
 "ট":"ट","ঠ":"ठ","ড":"ड","ঢ":"ढ","ণ":"ण","ত":"त","থ":"थ","দ":"द","ধ":"ध","ন":"न",
 "প":"प","ফ":"फ","ব":"ब","ভ":"भ","ম":"म","য":"य","র":"र","ল":"ल","শ":"श","ষ":"ष","স":"स","হ":"ह",
 "য়":"य","ড়":"ड़","ঢ়":"ढ़","ক্ষ":"क्ष","ৎ":"त्",
 "অ":"अ","আ":"आ","ই":"इ","ঈ":"ई","উ":"उ","ঊ":"ऊ","ঋ":"ऋ","এ":"ए","ঐ":"ऐ","ও":"ओ","ঔ":"औ",
}
VOWEL = {
 "া":"ा","ি":"ि","ী":"ी","ু":"ु","ূ":"ू","ৃ":"ृ","ে":"े","ৈ":"ੈ","ো":"ो","ৌ":"ौ","্":"्",
 "ঁ":"ँ","ং":"ं","ঃ":"ঃ","ঽ":"ऽ",
}

def bn_to_deva(s):
    out = []
    for ch in s:
        out.append(CONSO.get(ch, VOWEL.get(ch, ch)))
    return "".join(out)

def has_script(s, lo, hi):
    return any(lo <= ord(c) <= hi for c in s)

# ---------- 3. transcribe ----------
from faster_whisper import WhisperModel
model = WhisperModel("large-v3", device="cuda", compute_type="float16")
prog("large-v3 loaded on GPU")

hi_rows, en_rows, skipped = [], [], 0
for i, f in enumerate(cand, 1):
    try:
        segs, info = model.transcribe(f, language=None, beam_size=1, condition_on_previous_text=False)
        text = " ".join(s.text.strip() for s in segs).strip()
    except Exception:
        skipped += 1
        continue
    if len(text) < 4:
        skipped += 1
        continue
    beng = has_script(text, 0x0980, 0x09FF)
    deva = has_script(text, 0x0900, 0x097F)
    if beng:
        hi_rows.append((f, bn_to_deva(text)))
    elif deva:
        hi_rows.append((f, text))
    elif has_script(text, 32, 126):
        en_rows.append((f, text))
    else:
        skipped += 1
    if i % 250 == 0:
        prog(f"{i}/{len(cand)} hi={len(hi_rows)} en={len(en_rows)} skip={skipped} elapsed={int(time.time()-t0)}s")

# ---------- 4. write metadata (ljspeech pipe format) ----------
os.makedirs(os.path.join(WORK, "meta"), exist_ok=True)
with open(os.path.join(WORK, "meta", "metadata_hi.csv"), "w", encoding="utf-8") as fh:
    for p, t in hi_rows:
        fh.write(f"{p}|{t}\n")
with open(os.path.join(WORK, "meta", "metadata_en.csv"), "w", encoding="utf-8") as fh:
    for p, t in en_rows:
        fh.write(f"{p}|{t}\n")

zip_path = os.path.join(WORK, "xtts-meta.zip")
if os.path.exists(zip_path):
    os.remove(zip_path)
subprocess.run([sys.executable, "-m", "zipfile", "-c", zip_path, os.path.join(WORK, "meta")], capture_output=True)

prog(f"SAMPLES hi0={len(hi_rows[0][1]) if hi_rows else 0}ch en0={len(en_rows[0][1]) if en_rows else 0}ch")
prog(f"DONE total={len(cand)} hi={len(hi_rows)} en={len(en_rows)} skip={skipped} zip={os.path.getsize(zip_path)} elapsed={int(time.time()-t0)}s")
say(f"PREP_COMPLETE hi={len(hi_rows)} en={len(en_rows)} skip={skipped} - meta ready, pull xtts-meta.zip and bump father-corpus dataset")
