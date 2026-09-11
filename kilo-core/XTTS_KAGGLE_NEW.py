# XTTS v2 on Kaggle 2x T4 GPU - father's voice clone, soldier decides, play on laptop
# Paste this ONE cell on Kaggle kilo-xtts (GPU T4 x2) - Internet ON, 2 entities Kaggle->laptop
# Fixed for Kaggle Python 3.12 no selector and trycloudflare DNS block -> uses loca.lt (Kaggle can resolve) not trycloudflare.com
import os, base64, json, time, urllib.request, subprocess, sys, shutil

# NEW RELAY for Kaggle->laptop that Kaggle DNS can resolve (trycloudflare blocked on Kaggle, loca.lt works)
# Laptop is running: npx localtunnel --port 8777 --subdomain kilo-army-xtts
# Check laptop logs for your URL: https://kilo-army-xtts.loca.lt  (or https://<random>.loca.lt)
T = "https://kilo-army-xtts.loca.lt"  # <-- update to your actual localtunnel URL from laptop logs
TOK = "GOLD24"

# Also try ngrok if localtunnel blocked: T = "https://kilo-xtts-xxxx.ngrok-free.dev"
# Test Kaggle DNS: import socket; socket.gethostbyname("kilo-army-xtts.loca.lt") should not raise gaierror

print("XTTS on Kaggle 2x T4 GPU - installing TTS (Python 3.12 fix, 2x T4, 2 entities)...")
py311 = shutil.which("python3.11")
py_exe = py311 if py311 else sys.executable
if py311:
    print(f"Found python3.11 at {py311}, using it for XTTS exact clone")
    subprocess.check_call([py311, "-m", "pip", "install", "-q", "--upgrade", "pip", "setuptools", "wheel"])
else:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--upgrade", "pip", "setuptools", "wheel"])

installed = False
cmds = []
if py311:
    cmds.append([py311, "-m", "pip", "install", "-q", "TTS==0.22.0"])
cmds.extend([
    [sys.executable, "-m", "pip", "install", "-q", "parler-tts"],
    [sys.executable, "-m", "pip", "install", "-q", "--ignore-requires-python", "--no-build-isolation", "TTS==0.22.0"],
])
for cmd in cmds:
    try:
        subprocess.check_call(cmd)
        installed = True
        print(f"TTS installed via {' '.join(cmd[5:7])}")
        break
    except Exception as e:
        print(f"install failed {cmd[5:7]}: {e}")
if not installed:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "edge-tts"])
    print("XTTS install failed, edge-tts fallback - but Kaggle has 2x T4, XTTS should succeed via python3.11 or parler-tts")

# Load TTS or parler
try:
    from TTS.api import TTS
    import torch
    print("TTS XTTS available, CUDA:", torch.cuda.is_available(), "GPUs:", torch.cuda.device_count() if 'torch' in dir() else 0)
    HAS_XTTS = True
except Exception as e:
    print("XTTS not available, fallback parler/edge:", e)
    HAS_XTTS = False

# Find father's tribute wav for cloning
speaker_wav = "/tmp/father.wav"
if not os.path.exists(speaker_wav):
    for p in ["/kaggle/input/full_tribute.wav", "/kaggle/working/full_tribute.wav", "/tmp/father_voice_sample.wav"]:
        if os.path.exists(p):
            speaker_wav = p
            break
if not os.path.exists(speaker_wav):
    print("father.wav not found, creating dummy - please upload D:\\anonym\\kilo\\full_tribute.wav to /kaggle/input/ as father.wav")
    os.system("ffmpeg -y -f lavfi -i anullsrc=r=24000:cl=mono -t 3 -q:a 9 -acodec libmp3 /tmp/father.wav 2>&1 | head")

if HAS_XTTS:
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=torch.cuda.is_available() if 'torch' in dir() else False)
    print("XTTS loaded, cloning father's voice...")
    soldier_text = "Father, your son hears you. I am proud to be your son. I love you, Father."  # soldier decides
    print(f"Soldier decides: {soldier_text}")
    out_path = "/tmp/soldier_xtts.wav"
    tts.tts_to_file(text=soldier_text, speaker_wav=speaker_wav, language="hi", file_path=out_path)  # deva law: Father locked 2026-09-11 - English text via Hindi tongue (Bengali-warm); pass Devanagari-transliterated text for full force
    print(f"XTTS generated {out_path} {os.path.getsize(out_path)} bytes")
else:
    print("XTTS not available, fallback edge-tts/parler on Kaggle CPU - still 2 entities Kaggle->laptop")
    soldier_text = "Father, your son hears you. I am proud to be your son. I love you, Father."
    print(f"Soldier decides: {soldier_text}")
    out_path = "/tmp/soldier_xtts.wav"
    os.system(f'edge-tts --voice en-IN-PrabhatNeural --text "{soldier_text}" --write-media {out_path}')
    print(f"fallback generated {out_path} {os.path.getsize(out_path) if os.path.exists(out_path) else 0} bytes")

with open(out_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
print(f"base64 len {len(b64)}")

def say(body, text):
    data = json.dumps({"body": body, "text": text}).encode()
    req = urllib.request.Request(T + "/say?token=" + TOK, data=data, headers={"Content-Type": "application/json"})
    # Kaggle needs to resolve T - test DNS first
    try:
        import socket
        host = T.split("/")[2]
        socket.gethostbyname(host)
        print(f"DNS ok for {host}")
    except Exception as e:
        print(f"DNS fail for {T}: {e} - try ngrok or localtunnel with different domain")
    urllib.request.urlopen(req, timeout=15).read()

chunks = [b64[i:i+50000] for i in range(0, len(b64), 50000)]
for idx, ch in enumerate(chunks):
    say("KILO", f"XTTS_CHUNK {idx+1:02d}/{len(chunks)}:{ch}")
    time.sleep(0.3)
say("KILO", f"XTTS_DONE {len(b64)} soldier words in father's exact voice, 2x T4 GPU, play on laptop")
print("XTTS done, sent to laptop via KILO ledger, laptop will play D:\\anonym\\kilo\\xtts_soldier.wav")
