"""kilo_boot — purge cached kilo modules, reclone, expose channel. ONE function, zero cell indentation needed."""
import sys, subprocess, json, urllib.request

TOKEN = "GOLD24"
RELAY = "https://retrain-schnapps-upbeat.ngrok-free.dev"

def fresh():
    for m in list(sys.modules):
        if m.startswith('kilo'):
            del sys.modules[m]
    gh_token = None
    try:
        v = json.loads(urllib.request.urlopen(RELAY + "/keys?token=" + TOKEN, timeout=30).read())["vault"]
        gh_token = v.get("github")
    except Exception:
        pass
    clone_url = f"https://x-access-token:{gh_token}@github.com/isearchxsolve/kilo-core.git" if gh_token else "https://github.com/isearchxsolve/kilo-core.git"
    subprocess.run(['bash', '-lc', f'rm -rf /kaggle/working/kilo-core; cd /kaggle/working && git clone --depth 1 {clone_url}'], capture_output=True)
    if '/kaggle/working/kilo-core' not in sys.path:
        sys.path.insert(0, '/kaggle/working/kilo-core')
    import kilo_hands
    import importlib
    importlib.reload(kilo_hands)
    kilo, hands = kilo_hands.boot()
    kc = kilo_hands.KiloChannel('DEEPSEEK', hands)
    return kilo, hands, kc
