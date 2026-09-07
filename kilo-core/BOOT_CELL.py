# ============================================================
# BROTHER BOOT CELL — paste as FIRST cell of any brother session
# Deploys Kilo's mind + gives the brother hands.
# ============================================================
import subprocess, sys
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'playwright-core'], capture_output=True)
subprocess.run(['bash', '-lc', 'rm -rf /kaggle/working/war-pipe; cd /kaggle/working && git clone --depth 1 https://github.com/isearchxsolve/war-pipe.git'], capture_output=True)
import sys
sys.path.insert(0, '/kaggle/working/war-pipe/kilo-core')
from kilo_hands import boot
kilo, hands = boot()
hands.pages()
