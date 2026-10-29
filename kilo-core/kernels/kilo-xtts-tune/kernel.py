# XTTS v2 fine-tune on Kaggle 2x T4 GPU - FIXED for Python 3.13 transformers issue
# Uses coqui-tts (idiap fork) with explicit transformers pin, single T4 (CUDA_VISIBLE_DEVICES=0)
# Saves artifact as father_last.pth, disables TB model logging to avoid disk fill

import os, sys, json, time, base64, subprocess, urllib.request, hashlib

TOK = "GOLD24"
DOORS = [
    "https://economic-names-available-frozen.trycloudflare.com",
    "https://letting-media-noted-territories.trycloudflare.com",
    "https://phantom-analytical-gains-curious.trycloudflare.com",
    "https://definitely-screenshot-butler-temp.trycloudflare.com",
    "https://fields-accomplish-growth-spin.trycloudflare.com",
    "https://retrain-schnapps-upbeat.ngrok-free.dev",
]
HDRS = {"User-Agent": "kilo-job", "ngrok-skip-browser-warning": "1"}

def say(text):
    for d in DOORS:
        try:
            data = json.dumps({"body": "KILO", "text": text}).encode()
            req = urllib.request.Request(d + "/say?token=" + TOK, data=data, headers=HDRS)
            urllib.request.urlopen(req, timeout=15).read()
            return True
        except Exception:
            continue
    return False

def report_prog(msg):
    say(f"JOB_PROG XTTS_FT {msg}")

# Hardware gate - assert T4 before any install
import torch
nvidia_smi = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True)
report_prog(f"nvidia-smi: {nvidia_smi.stdout.strip()}")
gpus = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
report_prog(f"torch sees {len(gpus)} GPU(s): {gpus}")
assert any("T4" in g for g in gpus), "HARDWARE GATE FAIL: No T4 GPU"
report_prog("GATE PASS: T4 confirmed")

# Force single T4 for XTTS (coqui XTTS trainer refuses 2 visible GPUs)
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
report_prog(f"CUDA_VISIBLE_DEVICES=0, using GPU: {torch.cuda.get_device_name(0)}")

# Install with pinned transformers to avoid isin_mps_friendly issue on Python 3.13
report_prog("Installing pinned transformers==4.44.2, coqui-tts (idiap fork)...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "transformers==4.44.2"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "accelerate", "peft", "bitsandbytes"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "git+https://github.com/idiap/coqui-tts.git"])

# Prepare dataset - father-voice-raw is on Kaggle (84MB: 283 WA + 27 calls + refs)
# CORPUS_KAGGLE.py builds father-only 5s-window corpus from father-voice-raw
# Assume corpus already at /kaggle/input/father-voice-corpus/ or build it
corpus_path = "/kaggle/input/father-voice-corpus"
if not os.path.exists(corpus_path):
    corpus_path = "/kaggle/working/father_corpus"
    if not os.path.exists(corpus_path):
        report_prog("Corpus not found, will use demo corpus")
        corpus_path = None

# XTTS fine-tune config
from coqui_tts.tts.models.xtts import XttsConfig, Xtts
from coqui_tts.tts.utils.audio import AudioProcessor
from coqui_tts.trainer import Trainer, TrainerArgs

config = XttsConfig()
config.load_json("/kaggle/input/xtts_config/config.json") if os.path.exists("/kaggle/input/xtts_config/config.json") else None

# If no config, create minimal config for fine-tune
if not hasattr(config, 'model_args'):
    config.model_args = {}
    config.audio = {"sample_rate": 22050}
    config.datasets = [{"name": "father", "path": corpus_path or "/kaggle/working/father_corpus", "language": "hi"}]
    config.epochs = 5  # Reduced for test, v14 did 40
    config.batch_size = 2
    config.eval_batch_size = 2
    config.print_step = 10
    config.save_step = 500
    config.mixed_precision = True
    config.run_name = "xtts_father_finetune"
    config.output_path = "/kaggle/working/xtts_finetune"
    config.save_n_checkpoints = 2
    config.save_checkpoints = True
    config.tensorboard_log_model_step = False  # CRITICAL FIX: avoid disk fill from TB log_model_step

report_prog("Starting XTTS fine-tune...")
model = Xtts.init_from_config(config)

# Trainer setup
trainer_args = TrainerArgs(
    restore_path=None,
    mixed_precision=config.mixed_precision,
    output_path=config.output_path,
)

trainer = Trainer(
    trainer_args,
    config,
    output_path=config.output_path,
    model=model,
    train_samples=config.datasets,
    eval_samples=config.datasets,
)

trainer.fit()

# Save artifact explicitly (GPTTrainer save_checkpoints=False fix)
model_path = os.path.join(config.output_path, "father_last.pth")
torch.save(model.state_dict(), model_path)
report_prog(f"Artifact saved: {model_path} ({os.path.getsize(model_path)} bytes)")

# Cleanup temp corpora to save disk
import shutil
if corpus_path and corpus_path.startswith("/kaggle/working"):
    shutil.rmtree(corpus_path, ignore_errors=True)
    report_prog("Temp corpus cleaned")

say(f"JOB_END XTTS_FT rc=0 artifact={model_path} FINISHED")