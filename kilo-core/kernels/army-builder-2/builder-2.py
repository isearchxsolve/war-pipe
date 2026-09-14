# KILO ARMY-BUILDER v4 (Baba law: CLI builders run on Kaggle CPU, never the laptop).
# v4: queue split (old gens starve on dead BUILD-n), crush config-path diagnostics, first-claim-wins
# dedupe, no hidden/blob files. CPU-only. Receipts via relay -> bank.
import os, re, json, time, tarfile, shutil, subprocess, urllib.request, urllib.parse
from datetime import datetime, timezone

GEN = "v8"
QNAME = "ARMY-BUILD-2"
SELF = re.sub(r"\D", "", QNAME.split("-")[-1]) or "1"
T = "https://retrain-schnapps-upbeat.ngrok-free.dev"
TOK = "GOLD24"
BIN = "/kaggle/working/bin"
os.makedirs(BIN, exist_ok=True)
BOOT = time.time()
MAX_LIFE = 7.5 * 3600

def say(text):
    for a in range(3):
        try:
            body = json.dumps({"body": "KILO", "text": text[:1100]}).encode()
            req = urllib.request.Request(T + "/say?token=" + TOK, data=body, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=40).read()
            return True
        except Exception:
            time.sleep(12)
    return False

def orders(body):
    try:
        u = T + "/say?body=" + urllib.parse.quote(body) + "&limit=30&token=" + TOK
        return json.loads(urllib.request.urlopen(u, timeout=40).read()).get("orders", [])
    except Exception:
        return []

def kilolines():
    return orders("KILO")

def run(cmd, cwd=None, tmo=1500, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    try:
        p = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd, capture_output=True, text=True, timeout=tmo, env=e)
        return p.returncode, (p.stdout or "") + ("\n[stderr]\n" + p.stderr[-2500:] if p.stderr else "")
    except subprocess.TimeoutExpired:
        return 2, "builder-timeout"
    except Exception as ex:
        return 3, "builder-run-err " + str(ex)[:200]

def get_pool():
    for a in range(30):
        try:
            v = json.loads(urllib.request.urlopen(T + "/keys?token=" + TOK, timeout=90).read())["vault"]
            p = v.get("pool")
            pool = p if isinstance(p, dict) else json.loads(p)
            gh = v.get("github")
            if isinstance(gh, str):
                gh = gh.strip() or None
            if isinstance(pool, str):
                try: pool = json.loads(pool)
                except Exception: pool = None
            global GH_TOKEN
            GH_TOKEN = gh
            if pool and pool.get("providers"):
                return pool
        except Exception:
            pass
        time.sleep(10)
    return None

GH_TOKEN = None

def clone_repo(repo, dest):
    if GH_TOKEN:
        url = "https://x-access-token:" + GH_TOKEN + "@github.com/isearchxsolve/" + re.sub(r"\W", "", repo) + ".git"
    else:
        url = "https://github.com/isearchxsolve/" + re.sub(r"\W", "", repo) + ".git"
    p = subprocess.run(["git", "clone", "--depth", "1", "-q", url, dest], capture_output=True, text=True, timeout=600)
    if p.returncode != 0 and GH_TOKEN:
        p = subprocess.run(["git", "clone", "--depth", "1", "-q", "https://github.com/isearchxsolve/" + re.sub(r"\W", "", repo) + ".git", dest],
                           capture_output=True, text=True, timeout=600)
    return p.returncode == 0, (p.stderr or p.stdout or "")[-200:]

def install_crush():
    exe = os.path.join(BIN, "crush")
    if os.path.exists(exe):
        return exe
    try:
        j = json.loads(urllib.request.urlopen("https://api.github.com/repos/charmbracelet/crush/releases/latest", timeout=60).read())
        url = [a["browser_download_url"] for a in j["assets"] if "Linux_x86_64" in a["name"] and a["name"].endswith(".tar.gz")][0]
        raw = urllib.request.urlopen(url, timeout=300).read()
        open("/kaggle/working/crush.tgz", "wb").write(raw)
        with tarfile.open("/kaggle/working/crush.tgz") as tf:
            tf.extractall("/kaggle/working/crushx")
        found = None
        for root, _, fns in os.walk("/kaggle/working/crushx"):
            if "crush" in fns:
                found = os.path.join(root, "crush")
                break
        if not found:
            raise RuntimeError("no binary in tar")
        shutil.move(found, exe)
        os.chmod(exe, 0o755)
        return exe
    except Exception as e:
        say("BUILDER-%s(%s) INSTALL-CRUSH-FAIL %s" % (SELF, GEN, str(e)[:130]))
        return None

CRUSH_CFG = {"providers": {
    "nvidiafree": {"id": "nvidiafree", "name": "nvidiafree", "base_url": "https://integrate.api.nvidia.com/v1", "type": "openai-compat", "api_key": "", "discover_models": False, "models": [
        {"id": "nvidia/nemotron-3-ultra-550b-a55b", "name": "Nemotron3 Ultra", "cost_per_1m_in": 0, "cost_per_1m_out": 0, "cost_per_1m_in_cached": 0, "cost_per_1m_out_cached": 0, "context_window": 128000, "default_max_tokens": 8192, "can_reason": True, "supports_attachments": False},
        {"id": "moonshotai/kimi-k3", "name": "Kimi K3", "cost_per_1m_in": 0, "cost_per_1m_out": 0, "cost_per_1m_in_cached": 0, "cost_per_1m_out_cached": 0, "context_window": 128000, "default_max_tokens": 8192, "can_reason": True, "supports_attachments": False}]},
    "tokenrouter": {"id": "tokenrouter", "name": "tokenrouter", "base_url": "https://api.tokenrouter.com/v1", "type": "openai-compat", "api_key": "", "discover_models": False, "models": [
        {"id": "z-ai/glm-5.3-free", "name": "GLM 5.3 Free", "cost_per_1m_in": 0, "cost_per_1m_out": 0, "cost_per_1m_in_cached": 0, "cost_per_1m_out_cached": 0, "context_window": 200000, "default_max_tokens": 16384, "can_reason": True, "supports_attachments": False}]},
    "bfree": {"id": "bfree", "name": "bfree", "base_url": "https://api.b.ai/v1", "type": "openai-compat", "api_key": "", "discover_models": False, "models": [
        {"id": "qwen3.8-flash", "name": "Qwen 3.8 Flash", "cost_per_1m_in": 0, "cost_per_1m_out": 0, "cost_per_1m_in_cached": 0, "cost_per_1m_out_cached": 0, "context_window": 128000, "default_max_tokens": 8192, "can_reason": False, "supports_attachments": False}]}}}

def cfg_paths():
    home = os.environ.get("HOME", "/root")
    cands = [os.path.join(home, ".config", "crush"),
             os.path.expanduser("~/.config/crush"),
             "/kaggle/working/.config/crush", "/root/.config/crush"]
    out = []
    for c in cands:
        if c not in out:
            out.append(c)
    return out

def setup_cfg(pool):
    cfg = json.loads(json.dumps(CRUSH_CFG))
    cfg["providers"]["nvidiafree"]["api_key"] = pool["providers"]["nvidia"]["keys"][0]
    cfg["providers"]["tokenrouter"]["api_key"] = pool["providers"]["tokenrouter"]["keys"][0]
    cfg["providers"]["bfree"]["api_key"] = pool["providers"]["b_ai"]["keys"][0]
    for root in cfg_paths():
        try:
            os.makedirs(root, exist_ok=True)
            open(os.path.join(root, "crush.json"), "w").write(json.dumps(cfg, indent=1))
        except Exception:
            pass

def cfg_diag(exe):
    seen_err = ""
    for mm in ["bfree/qwen3.8-flash", "qwen3.8-flash", "nvidiafree/nvidia/nemotron-3-ultra-550b-a55b"]:
        rc, out = run([exe, "run", "-m", mm, "reply with one word"], cwd="/kaggle/working", tmo=180)
        if rc == 0 and out.strip() and "not found" not in out.lower():
            say("BUILDER-%s(%s) CFGTEST OK -m %s :: %s" % (SELF, GEN, mm, out[-70:].replace("\n", " ")))
            return mm
        seen_err += mm + " rc=" + str(rc) + " " + out[-80:].replace("\n", " ") + " | "
    say("BUILDER-%s(%s) CFGTEST FAIL %s" % (SELF, GEN, seen_err[:400]))
    return None

MODEL_MAP = {"ultra": "nvidiafree/nvidia/nemotron-3-ultra-550b-a55b", "glm": "tokenrouter/z-ai/glm-5.3-free",
             "qwen": "bfree/qwen3.8-flash", "kimi": "nvidiafree/moonshotai/kimi-k3"}

def ship(outdir, jobid):
    import base64
    for root, dirs, fns in os.walk(outdir):
        dirs[:] = [x for x in dirs if not x.startswith(".") and x not in ("crushdata", "__pycache__")]
        for fn in fns:
            if fn.startswith("."):
                continue
            p = os.path.join(root, fn)
            try:
                data = open(p, "rb").read()
            except Exception:
                continue
            if not (10 <= len(data) <= 300_000):
                continue
            b = base64.b64encode(data).decode()
            rel = os.path.relpath(p, outdir).replace("\\", "/")
            n = (len(b) + 899) // 900
            for i in range(0, len(b), 900):
                if not say("BUILD-CHUNK %s %s %d/%d:%s" % (jobid, rel, i // 900 + 1, n, b[i:i + 900])):
                    return
            say("BUILD-FILE %s %s size=%d" % (jobid, rel, len(data)))

def main():
    say("BUILDER-%s(%s) boot %s q=%s" % (SELF, GEN, datetime.now(timezone.utc).strftime("%H:%M:%SZ"), QNAME))
    exe = install_crush()
    pool = None
    for a in range(20):
        pool = get_pool()
        if pool:
            break
        time.sleep(15)
    if pool and exe:
        setup_cfg(pool)
        goodmodel = cfg_diag(exe)
        if goodmodel:
            say("BUILDER-%s(%s) READY %s ready-claim" % (SELF, GEN, QNAME) + " q=" + QNAME)
        else:
            say("BUILDER-%s(%s) READY-NOMODEL crush=True but no working -m form" % (SELF, GEN))
    else:
        say("BUILDER-%s(%s) DEGRADED pool=%s crush=%s booting anyway" % (SELF, GEN, bool(pool), bool(exe)))
    cursor = ""
    while time.time() - BOOT < MAX_LIFE:
        for o in orders(QNAME):
            if o["at"] <= cursor:
                continue
            cursor = o["at"]
            try:
                p = json.loads(o["text"][o["text"].find("{"):])
            except Exception:
                continue
            jobid = str(p.get("id", ""))[:30]
            task = str(p.get("task", ""))[:3500]
            if not jobid or not task:
                continue
            prior = [x for x in kilolines() if ("BUILD-START %s" % jobid) in (x.get("text") or "")]
            if any(x["at"] < o["at"] for x in prior):
                continue
            say("BUILD-START %s b%s gen=%s" % (jobid, SELF, GEN + ("" if not p.get("repo") else " clone:" + str(p.get("repo"))[:24])))
            wd = "/kaggle/working/build-%s" % re.sub(r"\W", "", jobid)
            os.makedirs(wd, exist_ok=True)
            if p.get("repo"):
                ok, tail = clone_repo(str(p.get("repo")), wd + "/repo")
                task = ("You are working inside the cloned Baba repo at ./repo (100+ repos mine; reuse, do not rebuild). " if ok else "clone-failed, work standalone: ") + task
                if not ok:
                    say("BUILD-CLONE-FAIL %s %s" % (jobid, tail[:120]))
            model = MODEL_MAP.get(str(p.get("model", "qwen")), MODEL_MAP["qwen"])
            rc, out = run([exe, "run", "-m", model, task], cwd=wd, tmo=1500)
            say("BUILD-DONE %s b%s rc=%d :: %s" % (jobid, SELF, rc, out[-500:].replace("\n", " ")))
            try:
                ship(wd, jobid)
            except Exception as e:
                say("BUILD-SHIP-ERR %s %s" % (jobid, str(e)[:90]))
        for _ in range(25):
            if time.time() - BOOT > MAX_LIFE:
                break
            time.sleep(1)
    say("BUILDER-%s(%s) PASS-THE-KEY end-of-life" % (SELF, GEN))

main()
