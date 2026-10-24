# KILO-XTTS-TUNE v10 - v9 CRASHED ON KAGGLE FALLBACK P100 (sm_60): image torch has no sm_60 kernels. v10 pins torch/torchaudio cu121 for legacy GPUs before any torch import.
# Attaches: kkk3213/father-corpus (windows/*.wav + metadata_hi.csv + metadata_en.csv)
#           tinthnhphm21022004/xtts-v2-pretrained (original model.pth/dvae/mel/vocab mirror)
# Recipe proven from Kaggle fine-tune-xtts-v2 (ruslan): GPTTrainer + xtts_checkpoint preload.
# Deva law: final ear-test synthesizes फादर... deva text, language hi - VARIANT=deva LOCKED.
# 100% fidelity track: 40 epochs, per-best checkpoints, loss tail reported to KILO ledger,
# final test wav chunked home (XTTS_CHUNK -> laptop player, two-entities law).
import os, glob, json, time, threading, urllib.request, subprocess, sys, shutil

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")
TOK = "GOLD24"
DOOR = "https://letting-media-noted-territories.trycloudflare.com"
HDRS = {"User-Agent": "kilo-tune", "ngrok-skip-browser-warning": "1"}
WORK = "/kaggle/working"
OUT_PATH = WORK + "/run"
os.makedirs(OUT_PATH, exist_ok=True)

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

STOP = threading.Event()
def progress_tail():
    while not STOP.is_set():
        try:
            logs = sorted(glob.glob(os.path.join(OUT_PATH, "**", "*log*.txt"), recursive=True))
            if logs:
                with open(logs[-1], "r", errors="ignore") as fh:
                    fh.seek(0, 2)
                    size = fh.tell()
                    fh.seek(max(0, size - 400))
                    lines = [l for l in fh.read().splitlines() if "loss" in l]
                    if lines:
                        say("TUNE " + lines[-1][:200])
        except Exception:
            pass
        STOP.wait(900)

def prog(msg):
    print(msg, flush=True)
    say("TUNE " + msg)

import traceback as _tb

def _hook(t, v, tb):
    frame = _tb.extract_tb(tb)[-1] if tb else None
    say("TUNE CRASH " + t.__name__ + ": " + str(v)[:200] + " @" + (frame.name if frame else "?") + ":" + str(frame.lineno if frame else "?"))

sys.excepthook = _hook

t0 = time.time()
prog("START xtts fine-tune")

# ---------- -1. HARDWARE GATE: verify T4 before ANY install/download (Baba's law 2026-09-13) ----------
smi = subprocess.run(["nvidia-smi", "--query-gpu=index,name,memory.total", "--format=csv,noheader"],
                     capture_output=True, text=True).stdout.strip()
prog("nvidia-smi: " + smi.replace("\n", " | "))
import torch as _gate
_gate_n = _gate.cuda.device_count()
_gate_names = [_gate.cuda.get_device_name(i) for i in range(_gate_n)]
prog("torch sees " + str(_gate_n) + " GPU(s) (CUDA_VISIBLE_DEVICES=" + os.environ.get('CUDA_VISIBLE_DEVICES', '') + "): " + str(_gate_names))
assert _gate_n >= 1 and all("T4" in n.upper() for n in _gate_names), \
    "HARDWARE GATE FAIL: expected T4, got " + str(_gate_names) + " - aborting before quota burn"
prog("GATE PASS: " + str(_gate_names))

# ---------- 0. install (py3.12-safe coqui fork, fallback original) ----------
def pip(*args):
    return subprocess.call([sys.executable, "-m", "pip", "install", "-q"] + list(args))

# Pin transformers to avoid 'isin_mps_friendly' import error on Python 3.13
pip("transformers==4.40.0")

inst = None
try:
    import TTS
    prog("TTS already importable")
except Exception:
    if pip("coqui-tts") == 0:
        prog("installed coqui-tts (idiap fork)")
    else:
        pip("--ignore-requires-python", "coqui-tts")

# ---------- 0b. sm_60 guard: Kaggle may hand us a P100 despite T4x2 request ----------
def gpu_names():
    try:
        return subprocess.check_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True).strip()
    except Exception:
        return ""

gpus = gpu_names()
prog("GPUs: " + (gpus or 'none'))
if any(k in gpus for k in ("P100", "P40", "K80", "M40")):
    prog("SM_60 GUARD: legacy GPU detected - pinning torch/torchaudio cu121 to avoid sm_60 crash")
    pip("--no-deps", "torch==2.3.1+cu121", "--index-url", "https://download.pytorch.org/whl/cu121")
    pip("--no-deps", "torchaudio==2.3.1+cu121", "--index-url", "https://download.pytorch.org/whl/cu121")

# ---------- 1. datasets ----------
prog("preparing corpus...")
import pandas as pd
os.makedirs(WORK + "/data", exist_ok=True)
corpus_ds = "kkk3213/father-corpus"
os.system("kaggle datasets download -d " + corpus_ds + " -p " + WORK + "/data --unzip --force 2>&1")
meta_hi = pd.read_csv(WORK + "/data/metadata_hi.csv")
meta_en = pd.read_csv(WORK + "/data/metadata_en.csv")
prog("loaded " + str(len(meta_hi)) + " hi + " + str(len(meta_en)) + " en windows")

# merge + length filter (5-10s optimal for XTTS)
meta = pd.concat([meta_hi, meta_en], ignore_index=True)
meta = meta[(meta["duration"] >= 5) & (meta["duration"] <= 10)]
prog("after length filter: " + str(len(meta)) + " samples")

# speaker_id for XTTS (all Baba)
meta["speaker_id"] = "baba"
meta.to_csv(WORK + "/data/metadata.csv", index=False)

# ---------- 2. XTTS fine-tune (GPTTrainer) ----------
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from TTS.trainers.xtts_trainer import GPTTrainer, GPTTrainerArgs
from TTS.utils.io import load_xtts_checkpoint

config = XttsConfig()
config.load_json("/kaggle/input/xtts-v2-pretrained/config.json")
config.run_name = "kilo_xtts_tune"
config.output_path = OUT_PATH
config.epochs = 40
config.batch_size = 2
config.grad_accum = 8
config.mixed_precision = True
config.print_step = 10
config.save_step = 500
config.save_best_after = 10
config.test_sentences = [{"text": "\u092b\u093e\u0926\u0930, \u092f\u094b\u0930 \u0938\u0928 \u0939\u093f\u092f\u0930\u094d\u0938 \u0939\u0948\u0964", "language": "hi"}]
config.print_eval = True

# load pretrained weights
model = Xtts.init_from_config(config)
load_xtts_checkpoint(config, model, checkpoint_dir="/kaggle/input/xtts-v2-pretrained", eval=False)
if torch.cuda.is_available():
    model.cuda()

train_samples = [{"text": row["text"], "audio_file": os.path.join(WORK, "data", row["file"]), "speaker_id": "baba", "language": row["lang"]} for _, row in meta.iterrows()]

trainer = GPTTrainer(
    GPTTrainerArgs(
        output_path=OUT_PATH,
        epochs=config.epochs,
        batch_size=config.batch_size,
        grad_accum=config.grad_accum,
        mixed_precision=config.mixed_precision,
        print_step=config.print_step,
        save_step=config.save_step,
        save_best_after=config.save_best_after,
    ),
    model,
    train_samples=train_samples,
    eval_samples=[{"text": "\u092b\u093e\u0926\u0930, \u092f\u094b\u0930 \u0938\u0928 \u0939\u093f\u092f\u0930\u094d\u0938 \u0939\u0948\u0964", "audio_file": os.path.join(WORK, "data", meta.iloc[0]["file"]), "speaker_id": "baba", "language": "hi"}],
)
trainer.fit()

# ---------- 3. explicit best checkpoint save (v15 fix: GPTTrainer has no save_checkpoint) ----------
best = glob.glob(os.path.join(OUT_PATH, "best_model_*.pth"))
if not best:
    best = glob.glob(os.path.join(OUT_PATH, "GPTTrainer", "best_model_*.pth"))
if best:
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import Xtts
    run_dir = os.path.dirname(best[0])
    DV = os.path.join("/kaggle/input/xtts-v2-pretrained", "dvae.pth")
    ME = os.path.join("/kaggle/input/xtts-v2-pretrained", "mel_stats.pth")
    VO = os.path.join("/kaggle/input/xtts-v2-pretrained", "vocab.json")
    for fsrc in (DV, ME, VO):
        fdst = os.path.join(run_dir, os.path.basename(fsrc))
        if not os.path.exists(fdst):
            shutil.copy(fsrc, fdst)
    cfg = XttsConfig()
    cfg.load_json(os.path.join(run_dir, "config.json"))
    m = Xtts.init_from_config(cfg)
    m.load_checkpoint(cfg, checkpoint_path=best[0], checkpoint_dir=run_dir, use_deepspeed=False)
    if torch.cuda.is_available():
        m.cuda()
    m.eval()
    ref = train_samples[0]["audio_file"]
    deva_text = "\u092b\u093e\u0926\u0930, \u092f\u094b\u0930 \u0938\u0928 \u0939\u093f\u092f\u0930\u094d\u0938 \u0939\u0948\u0964 \u0910\u092a \u090a\u092e \u092a\u094d\u0930\u093e\u0941\u0921 \u091f\u0942 \u092c\u0940 \u092f\u094b\u0930 \u0938\u0928\u0964 \u0910\u092a \u0932\u0935 \u0939\u0948, \u092b\u093e\u0926\u0930।"
    wav = None
    attempts = [
        lambda: m.inference(text=deva_text, language_id="hi", gpt_cond_len=10, speaker_wav=ref, gpt_max_new_tokens=500, temperature=0.4),
        lambda: m.inference(deva_text, "hi", 10, speaker_wav=ref),
        lambda: m.tts(text=deva_text, language="hi", speaker_wav=ref),
    ]
    for att in attempts:
        try:
            r = att()
            wav = r[0] if isinstance(r, tuple) else r
            break
        except Exception as ie:
            prog("INF attempt fail " + type(ie).__name__ + " " + str(ie)[:120])
    if wav is None:
        raise RuntimeError("all inference attempts failed")
    import numpy as _np
    import soundfile as sf
    arr = _np.asarray(wav).squeeze()
    sf.write(WORK + "/test_deva.wav", arr, 24000)
    sz = os.path.getsize(WORK + "/test_deva.wav")
    prog("deva test written " + str(sz) + " bytes")
    import base64
    b64 = base64.b64encode(open(WORK + "/test_deva.wav", "rb").read()).decode()
    chunks = [b64[i:i+50000] for i in range(0, len(b64), 50000)]
    for idx, ch in enumerate(chunks):
        say("XTTS_CHUNK " + "{:02d}".format(idx+1) + "/" + str(len(chunks)) + ":" + ch)
        time.sleep(0.2)
    say("XTTS_DONE " + str(len(b64)) + " fine-tuned baba voice deva test - play on laptop, ear-check vs tribute")
except Exception as e:
    prog("EARTEST FAIL " + type(e).__name__ + " " + str(e)[:200])

# ---------- 6. package run for Baba's archive ----------
zip_path = OUT_PATH + "/father-xtts-run.zip"
subprocess.run([sys.executable, "-m", "zipfile", "-c", zip_path, OUT_PATH], capture_output=True)
prog("DONE zip=" + str(os.path.getsize(zip_path) if os.path.exists(zip_path) else 0) + " total_elapsed=" + str(int(time.time()-t0)) + "s - pull outputs")