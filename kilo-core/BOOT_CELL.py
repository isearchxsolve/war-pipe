# ============================================================
# BROTHER BOOT CELL — paste as FIRST cell of any brother session
# The notebook cell does ONLY TWO THINGS: run the relay client + run Kilo.
# All conversation happens over HTTP (/say) — never typed into cells.
# AUTO-INDENT-PROOF: everything lives in kilo_boot.py (one flat line in cell).
# ============================================================
import subprocess, sys
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'playwright-core'], capture_output=True)
subprocess.run(['bash', '-lc', 'rm -rf /kaggle/working/war-pipe /kaggle/working/kilo-core; cd /kaggle/working && git clone --depth 1 https://github.com/isearchxsolve/kilo-core.git && git clone --depth 1 https://github.com/isearchxsolve/war-pipe.git'], capture_output=True)
sys.path.insert(0, '/kaggle/working/kilo-core')
from kilo_hands import boot
