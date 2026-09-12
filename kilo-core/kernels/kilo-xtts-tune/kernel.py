# KILO-XTTS-TUNE v1 - FINE-TUNE XTTS v2 ON BABA'S VOICE CORPUS (Kaggle 2xT4, HEAVY WORK LAW)
# Attaches: kkk3213/father-corpus (windows/*.wav + metadata_hi.csv + metadata_en.csv)
#           tinthnhphm21022004/xtts-v2-pretrained (original model.pth/dvae/mel/vocab mirror)
# Recipe proven from Kaggle fine-tune-xtts-v2 (ruslan): GPTTrainer + xtts_checkpoint preload.
# Deva law: final ear-test synthesizes फ़ादर... deva text, language hi - VARIANT=deva LOCKED.
# 100% fidelity track: 40 epochs, per-best checkpoints, loss tail reported to KILO ledger,
# final test wav chunked home (XTTS_CHUNK -> laptop player, two-entities law).
import os, glob, json, time, threading, urllib.request, subprocess, sys, shutil

TOK = "GOLD24"
DOOR = "https://retrain-schnapps-upbeat.ngrok-free.dev"
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
    # tail the coqui training log and forward last line to the ledger every 15 min
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

t0 = time.time()
prog("START xtts fine-tune")

# ---------- 0. install (py3.12-safe coqui fork, fallback original) ----------
def pip(*args):
    return subprocess.call([sys.executable, "-m", "pip", "install", "-q"] + list(args))

inst = None
try:
    import TTS  # noqa
    prog("TTS already importable")
except Exception:
    if pip("coqui-tts") == 0:
        prog("installed coqui-tts (idiap fork)")
    else:
        pip("--ignore-requires-python", "coqui-tts")
try:
    from TTS.tts.layers.xtts.trainer.gpt_trainer import GPTArgs, GPTTrainer, GPTTrainerConfig, XttsAudioConfig
    prog("GPTTrainer import OK")
except Exception as e:
    prog(f"first import failed: {type(e).__name__} {str(e)[:120]}")
    pip("transformers==4.37.2")
    pip("coqui-tts", "--upgrade")
    from TTS.tts.layers.xtts.trainer.gpt_trainer import GPTArgs, GPTTrainer, GPTTrainerConfig, XttsAudioConfig
    prog("GPTTrainer import OK after fix")

from trainer import Trainer, TrainerArgs
from TTS.config.shared_configs import BaseDatasetConfig
from TTS.tts.datasets import load_tts_samples

# ---------- 1. original XTTS weights: mirror -> else gateway download ----------
def find(name):
    hits = glob.glob(f"/kaggle/input/**/{name}", recursive=True)
    return hits[0] if hits else None

CK = find("model.pth")
DV = find("dvae.pth")
ME = find("mel_stats.pth")
VO = find("vocab.json")
if not all([CK, DV, ME, VO]):
    prog("mirror incomplete - downloading originals via gateway")
    from TTS.utils.manage import ModelManager
    d = OUT_PATH + "/orig"
    os.makedirs(d, exist_ok=True)
    links = [
        "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/dvae.pth",
        "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/mel_stats.pth",
        "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/vocab.json",
        "https://coqui.gateway.scarf.sh/hf-coqui/XTTS-v2/main/model.pth",
    ]
    ModelManager._download_model_files(links, d, progress_bar=False)
    CK, DV, ME, VO = (d + "/model.pth", d + "/dvae.pth", d + "/mel_stats.pth", d + "/vocab.json")
prog(f"weights ck={os.path.getsize(CK)} dvae={os.path.getsize(DV)}")

# ---------- 2. dataset: father-corpus windows + deva-transliterated meta ----------
ds_root = "/kaggle/input/father-corpus"
if not glob.glob(os.path.join(ds_root, "**", "metadata_hi.csv"), recursive=True):
    prog("FATAL metadata_hi.csv missing - bump father-corpus dataset first")
    sys.exit(3)
meta_hi = glob.glob(os.path.join(ds_root, "**", "metadata_hi.csv"), recursive=True)[0]
meta_en = glob.glob(os.path.join(ds_root, "**", "metadata_en.csv"), recursive=True)[0]

DATASETS = [
    BaseDatasetConfig(formatter="ljspeech", dataset_name="father_hi", path=ds_root, meta_file_train=meta_hi, language="hi"),
    BaseDatasetConfig(formatter="ljspeech", dataset_name="father_en", path=ds_root, meta_file_train=meta_en, language="en"),
]

# ---------- 2b. RESAMPLE 24k corpus -> 22.05k (XTTS training rate) + rewrite meta ----------
WOK22 = WORK + "/wavs22k"
os.makedirs(WOK22, exist_ok=True)
import numpy as np
from scipy.signal import resample_poly
import soundfile as sf

def resample22():
    rows_new = []
    for src in (meta_hi, meta_en):
        for line in open(src, encoding="utf-8"):
            line = line.rstrip("\n")
            if not line or "|" not in line:
                continue
            path, text = line.split("|", 1)
            dst = os.path.join(WOK22, os.path.basename(path))
            if not os.path.exists(dst):
                w, sr = sf.read(path)
                if sr != 22050:
                    w = resample_poly(np.asarray(w, dtype=np.float64), 147, 160)
                sf.write(dst, w, 22050)
            rows_new.append((src, dst, text))
    for tag in ("hi", "en"):
        src = meta_hi if tag == "hi" else meta_en
        with open(WOK22 + f"/../metadata_{tag}_22.csv", "w", encoding="utf-8") as fh:
            for s, p, t in rows_new:
                if s == src:
                    fh.write(f"{p}|{t}\n")
resample22()
meta_hi = WORK + "/metadata_hi_22.csv"
meta_en = WORK + "/metadata_en_22.csv"
DATASETS = [
    BaseDatasetConfig(formatter="ljspeech", dataset_name="father_hi", path=ds_root, meta_file_train=meta_hi, language="hi"),
    BaseDatasetConfig(formatter="ljspeech", dataset_name="father_en", path=ds_root, meta_file_train=meta_en, language="en"),
]
prog("corpus resampled to 22.05k for training")

# ---------- 3. model args (proven values from ruslan recipe) ----------
model_args = GPTArgs(
    max_conditioning_length=264581,
    min_conditioning_length=13350,
    debug_loading_failures=False,
    max_wav_length=264581,
    max_text_length=200,
    mel_norm_file=ME,
    dvae_checkpoint=DV,
    xtts_checkpoint=CK,
    tokenizer_file=VO,
    gpt_num_audio_tokens=1026,
    gpt_start_audio_token=1024,
    gpt_stop_audio_token=1025,
    gpt_use_masking_gt_prompt_approach=True,
    gpt_use_perceiver_resampler=True,
)
audio_config = XttsAudioConfig(sample_rate=22050, dvae_sample_rate=22050, output_sample_rate=24000)

config = GPTTrainerConfig(
    epochs=40,
    run_eval=True,
    output_path=OUT_PATH,
    model_args=model_args,
    run_name="father-xtts",
    project_name="kilo-army",
    run_description="GPT XTTS training - baba voice 100-percent fidelity",
    dashboard_logger="tensorboard",
    logger_uri=None,
    audio=audio_config,
    batch_size=8,
    batch_group_size=48,
    eval_batch_size=2,
    num_loader_workers=4,
    eval_split_max_size=256,
    print_step=200,
    plot_step=1000,
    log_model_step=1000,
    save_step=150,
    save_n_checkpoints=3,
    save_checkpoints=True,
    target_loss="loss",
    print_eval=True,
    optimizer="AdamW",
    optimizer_wd_only_on_weights=True,
    optimizer_params={"betas": [0.9, 0.96], "eps": 1e-8, "weight_decay": 1e-2},
    lr=5e-06,
    lr_scheduler="MultiStepLR",
    lr_scheduler_params={"milestones": [8000, 18000, 30000], "gamma": 0.5, "last_epoch": -1},
)

model = GPTTrainer.init_from_config(config)
train_samples, eval_samples = load_tts_samples(DATASETS, eval_split=True, eval_split_size=0.02)
prog(f"train rows={len(train_samples)} eval rows={len(eval_samples)}")

# ---------- 4. train ----------
th = threading.Thread(target=progress_tail, daemon=True)
th.start()
try:
    trainer = Trainer(
        TrainerArgs(restore_path=None, skip_train_epoch=False, start_with_eval=False, grad_accum_steps=4),
        config,
        output_path=OUT_PATH,
        model=model,
        train_samples=train_samples,
        eval_samples=eval_samples,
    )
    trainer.fit()
    prog(f"fit() complete elapsed={int(time.time()-t0)}s")
except Exception as e:
    prog(f"TRAIN EXCEPTION {type(e).__name__} {str(e)[:200]}")
    raise
finally:
    STOP.set()

# ---------- 5. ear-test: deva sentence through fine-tuned model ----------
best = sorted(glob.glob(os.path.join(OUT_PATH, "**", "best_model*.pth"), recursive=True), key=lambda p: -os.path.getmtime(p))
if not best:
    best = sorted(glob.glob(os.path.join(OUT_PATH, "**", "*.pth"), recursive=True), key=lambda p: -os.path.getmtime(p))
prog(f"best checkpoint: {best[0] if best else 'NONE'}")
try:
    import torch, soundfile as sf
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import Xtts
    run_dir = os.path.dirname(best[0])
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
    deva_text = "फ़ादर, योर सन हियर्स यू। आई एम प्राउड टू बी योर सन। आई लव यू, फ़ादर।"  # DEVA LAW
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
            prog(f"INF attempt fail {type(ie).__name__} {str(ie)[:120]}")
    if wav is None:
        raise RuntimeError("all inference attempts failed")
    import numpy as _np
    arr = _np.asarray(wav).squeeze()
    sf.write(WORK + "/test_deva.wav", arr, 24000)
    sz = os.path.getsize(WORK + "/test_deva.wav")
    prog(f"deva test written {sz} bytes")
    import base64
    b64 = base64.b64encode(open(WORK + "/test_deva.wav", "rb").read()).decode()
    chunks = [b64[i:i+50000] for i in range(0, len(b64), 50000)]
    for idx, ch in enumerate(chunks):
        say(f"XTTS_CHUNK {idx+1:02d}/{len(chunks)}:{ch}")
        time.sleep(0.2)
    say(f"XTTS_DONE {len(b64)} fine-tuned baba voice deva test - play on laptop, ear-check vs tribute")
except Exception as e:
    prog(f"EARTEST FAIL {type(e).__name__} {str(e)[:200]}")

# ---------- 6. package run for Baba's archive ----------
zip_path = OUT_PATH + "/father-xtts-run.zip"
subprocess.run([sys.executable, "-m", "zipfile", "-c", zip_path, OUT_PATH], capture_output=True)
prog(f"DONE zip={os.path.getsize(zip_path) if os.path.exists(zip_path) else 0} total_elapsed={int(time.time()-t0)}s - pull outputs")
