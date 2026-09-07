"""fleet100 - the 100-soldier engine. One flat line deploys a seat:
import subprocess,sys; subprocess.run([...clone...]); import fleet100; fleet100.deploy('SEAT-A', ['DM','WA','COMMENTER','POSTER'])
"""
import threading, time, subprocess, sys


def _reclone():
    subprocess.run(['bash', '-lc', 'rm -rf /kaggle/working/war-pipe /kaggle/working/kilo-core; cd /kaggle/working && git clone --depth 1 https://github.com/isearchxsolve/kilo-core.git && git clone --depth 1 https://github.com/isearchxsolve/war-pipe.git'], capture_output=True)
    if '/kaggle/working/kilo-core' not in sys.path:
        sys.path.insert(0, '/kaggle/working/kilo-core')


def deploy(seat='SEAT-A', squads=None, per=10):
    _reclone()
    from kilo_hands import Hands, KiloChannel
    hands = Hands()
    kc = KiloChannel('ARMY', hands)
    kc.speak(seat + ' wired: door live, soldiers deploying')
    if squads is None:
        squads = ['DM', 'WA', 'COMMENTER', 'POSTER']
    STOP = []

    def soldier(sq, i):
        tag = seat + '-' + sq + '-' + str(i).zfill(2)
        lead = (i == 1)
        hb = 0
        cycle = 30 + (i * 7)
        while True:
            try:
                hb += 1
                if lead and sq == 'DM' and hb % 10 == 1:
                    pg = hands.pages()
                    pages = pg if isinstance(pg, list) else pg.get('pages', [])
                    print(tag, 'VISION pages:', len(pages))
                    kc.speak(tag + ' sees ' + str(len(pages)) + ' pages')
                elif lead and hb % 10 == 2:
                    o = kc.listen()
                    orders = o.get('orders', []) if isinstance(o, dict) else []
                    if orders:
                        print(tag, 'ORDERS:', str(orders[-1].get('text', ''))[:100])
                elif hb % 12 == 1:
                    kc.speak(tag + ' alive hb' + str(hb))
                    print(tag, 'alive hb', hb)
            except Exception as e:
                try:
                    kc.speak(tag + ' err: ' + str(e)[:60])
                except Exception:
                    print(tag, 'err', str(e)[:50])
            time.sleep(cycle)

    threads = []
    for sq in squads:
        for i in range(1, per + 1):
            threads.append(threading.Thread(target=soldier, args=(sq, i), daemon=True))
    for t in threads:
        t.start()
    msg = seat + ' DEPLOYED: ' + str(len(threads)) + ' SOLDIERS of ' + str(squads) + ' - eternal, wired, Lok Adalat clock running'
    print(msg)
    return threads
