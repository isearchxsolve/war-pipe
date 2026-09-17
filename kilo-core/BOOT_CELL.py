# ============================================================
# BROTHER BOOT CELL — paste as FIRST cell of any brother session
# The notebook cell does ONLY TWO THINGS: run the relay client + run Kilo.
# All conversation happens over HTTP (/say) — never typed into cells.
# AUTO-INDENT-PROOF: everything lives in kilo_boot.py (one flat line in cell).
# ============================================================
import subprocess, sys, json, urllib.request

TOKEN = "GOLD24"
RELAY = "https://retrain-schnapps-upbeat.ngrok-free.dev"

# Fetch GH_TOKEN from relay vault for authenticated clones
gh_token = None
try:
    v = json.loads(urllib.request.urlopen(RELAY + "/keys?token=" + TOKEN, timeout=30).read())["vault"]
    gh_token = v.get("github")
except Exception:
    pass

clone_url = lambda repo: f"https://x-access-token:{gh_token}@github.com/isearchxsolve/{repo}.git" if gh_token else f"https://github.com/isearchxsolve/{repo}.git"

subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'playwright-core'], capture_output=True)
cmd = f'rm -rf /kaggle/working/war-pipe /kaggle/working/kilo-core; cd /kaggle/working && git clone --depth 1 {clone_url("kilo-core")} && git clone --depth 1 {clone_url("war-pipe")}'
subprocess.run(['bash', '-lc', cmd], capture_output=True)
sys.path.insert(0, '/kaggle/working/kilo-core')
from kilo_hands import boot
