"""kilo_boot — purge cached kilo modules, reclone, expose channel. ONE function, zero cell indentation needed."""
import sys, subprocess

def fresh():
    for m in list(sys.modules):
        if m.startswith('kilo'):
            del sys.modules[m]
    subprocess.run(['bash', '-lc', 'rm -rf /kaggle/working/kilo-core; cd /kaggle/working && git clone --depth 1 https://github.com/isearchxsolve/kilo-core.git'], capture_output=True)
    if '/kaggle/working/kilo-core' not in sys.path:
        sys.path.insert(0, '/kaggle/working/kilo-core')
    import kilo_hands
    import importlib
    importlib.reload(kilo_hands)
    kilo, hands = kilo_hands.boot()
    kc = kilo_hands.KiloChannel('DEEPSEEK', hands)
    return kilo, hands, kc
