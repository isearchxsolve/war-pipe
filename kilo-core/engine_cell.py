# KILO ENGINES v4.2 DUTIES-BAKED - multiple engines per Kaggle instance, hands = FATHERS CHROME via relay
import base64, sys, os, subprocess, time, json, threading, urllib.request, urllib.parse
ENGINE_SRC = base64.b64decode("aW1wb3J0IHN5cywgb3MsIGpzb24sIHRpbWUsIHRocmVhZGluZywgcXVldWUsIHVybGxpYi5yZXF1ZXN0LCByZQpmcm9tIGh0dHAuc2VydmVyIGltcG9ydCBCYXNlSFRUUFJlcXVlc3RIYW5kbGVyLCBUaHJlYWRpbmdIVFRQU2VydmVyCgpFTkdJTkVfTkFNRSA9IHN5cy5hcmd2WzFdIGlmIGxlbihzeXMuYXJndikgPiAxIGVsc2UgIkVOR0lORS0xIgpQT1JUID0gaW50KHN5cy5hcmd2WzJdKSBpZiBsZW4oc3lzLmFyZ3YpID4gMiBlbHNlIDk5OTkKVFVOTkVMID0gc3lzLmFyZ3ZbM10gaWYgbGVuKHN5cy5hcmd2KSA+IDMgZWxzZSAiIgpUT0tFTiA9ICJHT0xEMjQiClBSRUZfS1cgPSBvcy5lbnZpcm9uLmdldCgiRU5HSU5FX0tXIiwgImxpbmtlZGluIikKUEFHRV9DQUNIRSA9IHsicGFnZUlkIjogTm9uZX0KCmRlZiByYXdfdG9vbChuYW1lLCBhcmdzKToKICAgIHIgPSB1cmxsaWIucmVxdWVzdC5SZXF1ZXN0KFRVTk5FTCArICIvdG9vbD90b2tlbj0iICsgVE9LRU4sIGRhdGE9anNvbi5kdW1wcyh7Im5hbWUiOiBuYW1lLCAiYXJndW1lbnRzIjogYXJnc30pLmVuY29kZSgpLCBoZWFkZXJzPXsiQ29udGVudC1UeXBlIjogImFwcGxpY2F0aW9uL2pzb24ifSkKICAgIHJlcyA9IGpzb24ubG9hZHModXJsbGliLnJlcXVlc3QudXJsb3BlbihyLCB0aW1lb3V0PTEyMCkucmVhZCgpKQogICAgYyA9IHJlcy5nZXQoInJlc3VsdCIsIHt9KS5nZXQoImNvbnRlbnQiLCBbXSkKICAgIGVyciA9IHJlcy5nZXQoInJlc3VsdCIsIHt9KS5nZXQoImlzRXJyb3IiLCBGYWxzZSkKICAgIHJldHVybiBlcnIsIChjWzBdLmdldCgidGV4dCIsICIiKSBpZiBjIGFuZCBpc2luc3RhbmNlKGMsIGxpc3QpIGVsc2Ugc3RyKHJlcykpWzoxMjAwMF0KCmRlZiByZXNvbHZlX3BhZ2Uoa3cpOgogICAgZXJyLCB0eHQgPSByYXdfdG9vbCgibGlzdF9wYWdlcyIsIHt9KQogICAgZm9yIGxpbmUgaW4gc3RyKHR4dCkuc3BsaXRsaW5lcygpOgogICAgICAgIG0gPSByZS5tYXRjaChyIlxzKihcZCspOiIsIGxpbmUpCiAgICAgICAgaWYgbSBhbmQga3cgaW4gbGluZS5sb3dlcigpOgogICAgICAgICAgICByZXR1cm4gaW50KG0uZ3JvdXAoMSkpCiAgICBsaW5lcyA9IFtsIGZvciBsIGluIHN0cih0eHQpLnNwbGl0bGluZXMoKSBpZiByZS5tYXRjaChyIlxzKlxkKzoiLCBsKV0KICAgIGlmIGxpbmVzOgogICAgICAgIG0gPSByZS5tYXRjaChyIlxzKihcZCspOiIsIGxpbmVzWzBdKQogICAgICAgIHJldHVybiBpbnQobS5ncm91cCgxKSkKICAgIHJldHVybiAxCgpkZWYgZ2V0X3BhZ2VfaWQoa3cpOgogICAgaWYgUEFHRV9DQUNIRVsicGFnZUlkIl0gaXMgTm9uZToKICAgICAgICBQQUdFX0NBQ0hFWyJwYWdlSWQiXSA9IHJlc29sdmVfcGFnZShrdyBvciBQUkVGX0tXKQogICAgcmV0dXJuIFBBR0VfQ0FDSEVbInBhZ2VJZCJdCgpDTURTID0gcXVldWUuUXVldWUoKQpSRVNVTFRTID0ge30KUklEID0gWzBdClJMT0NLID0gdGhyZWFkaW5nLkxvY2soKQoKZGVmIGVuZ2luZV9tYWluKCk6CiAgICB3aGlsZSBUcnVlOgogICAgICAgIHJpZCwgdG5hbWUsIHRhcmdzID0gQ01EUy5nZXQoKQogICAgICAgIHRyeToKICAgICAgICAgICAgb3V0ID0gcmF3X3Rvb2wodG5hbWUsIHRhcmdzKQogICAgICAgICAgICBSRVNVTFRTW3JpZF0gPSAoVHJ1ZSwgb3V0KQogICAgICAgIGV4Y2VwdCBFeGNlcHRpb24gYXMgZToKICAgICAgICAgICAgUkVTVUxUU1tyaWRdID0gKEZhbHNlLCBzdHIoZSlbOjIwMF0pCgp0aHJlYWRpbmcuVGhyZWFkKHRhcmdldD1lbmdpbmVfbWFpbiwgZGFlbW9uPVRydWUpLnN0YXJ0KCkKCkhBTkRfQUxJQVNFUyA9IHsKICAgICJuYXZpZ2F0ZSI6ICgibmF2aWdhdGVfcGFnZSIsIGxhbWJkYSBhOiB7InR5cGUiOiAidXJsIiwgInVybCI6IGEuZ2V0KCJ1cmwiLCAiYWJvdXQ6YmxhbmsiKSwgInBhZ2VJZCI6IGEuZ2V0KCJwYWdlSWQiLCBnZXRfcGFnZV9pZChhLmdldCgia3ciLCAiIikpKX0pLAogICAgImxpc3RfcGFnZXMiOiAoImxpc3RfcGFnZXMiLCBsYW1iZGEgYToge30pLAogICAgInNuYXBzaG90IjogKCJ0YWtlX3NuYXBzaG90IiwgbGFtYmRhIGE6IHsicGFnZUlkIjogYS5nZXQoInBhZ2VJZCIsIGdldF9wYWdlX2lkKGEuZ2V0KCJrdyIsICIiKSkpfSksCiAgICAiY2xpY2siOiAoImNsaWNrIiwgbGFtYmRhIGE6IHsidWlkIjogYS5nZXQoInVpZCIpLCAicGFnZUlkIjogYS5nZXQoInBhZ2VJZCIsIGdldF9wYWdlX2lkKGEuZ2V0KCJrdyIsICIiKSkpfSksCiAgICAidHlwZV90ZXh0IjogKCJ0eXBlX3RleHQiLCBsYW1iZGEgYTogeyJ0ZXh0IjogYS5nZXQoInRleHQiLCAiIiksICJwYWdlSWQiOiBhLmdldCgicGFnZUlkIiwgZ2V0X3BhZ2VfaWQoYS5nZXQoImt3IiwgIiIpKSl9KSwKICAgICJrZXkiOiAoInByZXNzX2tleSIsIGxhbWJkYSBhOiB7ImtleSI6IGEuZ2V0KCJrZXkiLCAiRW50ZXIiKSwgInBhZ2VJZCI6IGEuZ2V0KCJwYWdlSWQiLCBnZXRfcGFnZV9pZChhLmdldCgia3ciLCAiIikpKX0pLAogICAgImV2YWwiOiAoImV2YWx1YXRlX3NjcmlwdCIsIGxhbWJkYSBhOiB7ImZ1bmN0aW9uIjogYS5nZXQoImpzIiwgYS5nZXQoImZ1bmN0aW9uIiwgIigpID0+IGRvY3VtZW50LnRpdGxlIikpLCAicGFnZUlkIjogYS5nZXQoInBhZ2VJZCIsIGdldF9wYWdlX2lkKGEuZ2V0KCJrdyIsICIiKSkpfSksCiAgICAidGl0bGUiOiAoImV2YWx1YXRlX3NjcmlwdCIsIGxhbWJkYSBhOiB7ImZ1bmN0aW9uIjogIigpID0+IGRvY3VtZW50LnRpdGxlIiwgInBhZ2VJZCI6IGEuZ2V0KCJwYWdlSWQiLCBnZXRfcGFnZV9pZChhLmdldCgia3ciLCAiIikpKX0pLAp9CgpjbGFzcyBIKEJhc2VIVFRQUmVxdWVzdEhhbmRsZXIpOgogICAgZGVmIGxvZ19tZXNzYWdlKHNlbGYsICphKToKICAgICAgICBwYXNzCgogICAgZGVmIGRvX1BPU1Qoc2VsZik6CiAgICAgICAgaWYgc2VsZi5wYXRoICE9ICIvaGFuZHMiOgogICAgICAgICAgICBzZWxmLnNlbmRfcmVzcG9uc2UoNDA0KQogICAgICAgICAgICBzZWxmLmVuZF9oZWFkZXJzKCkKICAgICAgICAgICAgcmV0dXJuCiAgICAgICAgbiA9IGludChzZWxmLmhlYWRlcnMuZ2V0KCJDb250ZW50LUxlbmd0aCIsIDApKQogICAgICAgIHRyeToKICAgICAgICAgICAgcmVxID0ganNvbi5sb2FkcyhzZWxmLnJmaWxlLnJlYWQobikpCiAgICAgICAgICAgIG5hbWUgPSByZXEuZ2V0KCJuYW1lIikKICAgICAgICAgICAgYXJncyA9IHJlcS5nZXQoImFyZ3VtZW50cyIsIHt9KQogICAgICAgICAgICBpZiBuYW1lIGluIEhBTkRfQUxJQVNFUzoKICAgICAgICAgICAgICAgIHRuYW1lLCBhcmdmID0gSEFORF9BTElBU0VTW25hbWVdCiAgICAgICAgICAgICAgICB0YXJncyA9IHtrOiB2IGZvciBrLCB2IGluIGFyZ2YoYXJncykuaXRlbXMoKSBpZiB2IGlzIG5vdCBOb25lfQogICAgICAgICAgICBlbHNlOgogICAgICAgICAgICAgICAgdG5hbWUsIHRhcmdzID0gbmFtZSwgYXJncwogICAgICAgICAgICB3aXRoIFJMT0NLOgogICAgICAgICAgICAgICAgUklEWzBdICs9IDEKICAgICAgICAgICAgICAgIHJpZCA9IFJJRFswXQogICAgICAgICAgICBDTURTLnB1dCgocmlkLCB0bmFtZSwgdGFyZ3MpKQogICAgICAgICAgICBmb3IgXyBpbiByYW5nZSgyNDApOgogICAgICAgICAgICAgICAgaWYgcmlkIGluIFJFU1VMVFM6CiAgICAgICAgICAgICAgICAgICAgYnJlYWsKICAgICAgICAgICAgICAgIHRpbWUuc2xlZXAoMC41KQogICAgICAgICAgICBvaywgb3V0ID0gUkVTVUxUUy5wb3AocmlkLCAoRmFsc2UsICJ0aW1lb3V0IikpCiAgICAgICAgICAgIGlmIChub3Qgb2spIG9yICgiaXNFcnJvciIgaW4gc3RyKG91dClbOjgwXSkgb3IgKCJJbnZhbGlkIGFyZ3VtZW50cyIgaW4gc3RyKG91dClbOjE1MF0pIG9yICgiUmVxdWlyZWQgYXQgcGFnZUlkIiBpbiBzdHIob3V0KSk6CiAgICAgICAgICAgICAgICBQQUdFX0NBQ0hFWyJwYWdlSWQiXSA9IE5vbmUKICAgICAgICAgICAgICAgIHRyeToKICAgICAgICAgICAgICAgICAgICBQQUdFX0NBQ0hFWyJwYWdlSWQiXSA9IHJlc29sdmVfcGFnZShhcmdzLmdldCgia3ciLCBQUkVGX0tXKSkKICAgICAgICAgICAgICAgIGV4Y2VwdCBFeGNlcHRpb246CiAgICAgICAgICAgICAgICAgICAgcGFzcwogICAgICAgICAgICBib2R5ID0ganNvbi5kdW1wcyh7Im9rIjogVHJ1ZSwgInJlc3VsdCI6IHN0cihvdXQpfSkuZW5jb2RlKCkKICAgICAgICBleGNlcHQgRXhjZXB0aW9uIGFzIGU6CiAgICAgICAgICAgIGJvZHkgPSBqc29uLmR1bXBzKHsib2siOiBGYWxzZSwgImVycm9yIjogc3RyKGUpWzoyMDBdfSkuZW5jb2RlKCkKICAgICAgICBzZWxmLnNlbmRfcmVzcG9uc2UoMjAwKQogICAgICAgIHNlbGYuc2VuZF9oZWFkZXIoIkNvbnRlbnQtVHlwZSIsICJhcHBsaWNhdGlvbi9qc29uIikKICAgICAgICBzZWxmLnNlbmRfaGVhZGVyKCJDb250ZW50LUxlbmd0aCIsIHN0cihsZW4oYm9keSkpKQogICAgICAgIHNlbGYuZW5kX2hlYWRlcnMoKQogICAgICAgIHNlbGYud2ZpbGUud3JpdGUoYm9keSkKCnByaW50KEVOR0lORV9OQU1FLCAiaGFuZHMtcHJveHkgdXAgb24gcG9ydCIsIFBPUlQsICItPiBGQVRIRVJTIENIUk9NRSB2aWEgcmVsYXksIGt3PSIgKyBQUkVGX0tXLCBmbHVzaD1UcnVlKQpUaHJlYWRpbmdIVFRQU2VydmVyKCgiMTI3LjAuMC4xIiwgUE9SVCksIEgpLnNlcnZlX2ZvcmV2ZXIoKQo=").decode()
with open("/kaggle/working/kilo_engine_server.py", "w") as f:
    f.write(ENGINE_SRC)
TUNNEL = "https://delivering-syndicate-musician-charge.trycloudflare.com"

def post(p, d):
    r = urllib.request.Request(TUNNEL + p + "?token=GOLD24", data=json.dumps(d).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=30).read())

def get(p):
    return json.loads(urllib.request.urlopen(TUNNEL + p + "?token=GOLD24", timeout=30).read())

def speak(tag, txt):
    try:
        post("/say", {"body": tag, "text": txt})
    except Exception as e:
        print(tag, "speak-fail", str(e)[:40])

def hear(sq):
    try:
        return get("/hear?body=" + urllib.parse.quote(sq)).get("reports", [])
    except Exception:
        return []

def hand(port, name, args):
    r = urllib.request.Request("http://127.0.0.1:%d/hands" % port, data=json.dumps({"name": name, "arguments": args}).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=150).read())

ENGINES = [
    ("ENGINE-1", 9999, "SEAT-A", ["DM", "WA", "COMMENTER", "POSTER"], 10, "linkedin"),
    ("ENGINE-2", 9998, "SEAT-B", ["BIZMODEL", "MONITOR", "SCOUT"], 10, "naukri"),
    ("ENGINE-3", 9997, "SEAT-C", ["LEDGER", "HERALD", "WARDEN"], 10, "whatsapp"),
]
PROCS = {}
for name, port, seat, squads, per, kw in ENGINES:
    env = dict(os.environ)
    env["ENGINE_KW"] = kw
    p = subprocess.Popen([sys.executable, "/kaggle/working/kilo_engine_server.py", name, str(port), TUNNEL], env=env)
    PROCS[name] = p
    print(name, "spawned pid", p.pid, "port", port, "kw", kw)
print("waiting for engines...")
time.sleep(12)
for name, port, seat, squads, per, kw in ENGINES:
    p = PROCS[name]
    if p.poll() is not None:
        print(name, "DIED rc", p.returncode)
        speak("ENGINE", name + " DIED " + str(p.returncode))
    else:
        print(name, "ALIVE hands-proxy -> fathers chrome")


JS_LI_THREADS = """() => { const t=Array.from(document.querySelectorAll('li.msg-conversation-listitem, [data-conversation-id]')); const out=[]; t.slice(0,8).forEach(x=>{out.push(x.textContent.replace(/\\s+/g,' ').trim().substring(0,60));}); return JSON.stringify(out); }"""
JS_NAUKRI_JOBS = """() => { const t=Array.from(document.querySelectorAll('[class*=jobTitle], h2, h3')).map(x=>x.textContent.replace(/\\s+/g,' ').trim()).filter(x=>x&&x.length>15&&x.length<90); return JSON.stringify(t.slice(0,8)); }"""
JS_GMAIL_SUBJ = """() => { const rows=Array.from(document.querySelectorAll('tr.zA')).slice(0,8); const out=[]; rows.forEach(r=>{const s=r.querySelector('.yP, .zF'); const sub=r.querySelector('.bog'); out.push((s?s.textContent.trim():'?')+' :: '+(sub?sub.textContent.trim().substring(0,60):'?'));}); return JSON.stringify(out); }"""

def hunt_naukri(port):
    hand(port, "navigate", {"url": "https://www.naukri.com/ai-engineer-remote-jobs", "kw": "naukri"})
    time.sleep(5)
    out = hand(port, "eval", {"js": JS_NAUKRI_JOBS, "kw": "naukri"})
    return "HUNT " + str(out)[:200]

def triage_linkedin(port):
    hand(port, "navigate", {"url": "https://www.linkedin.com/messaging/", "kw": "linkedin"})
    time.sleep(5)
    out = hand(port, "eval", {"js": JS_LI_THREADS, "kw": "linkedin"})
    return "TRIAGE " + str(out)[:200]

def watch_family(port):
    out = hand(port, "eval", {"js": "() => document.title", "kw": "whatsapp"})
    return "FAMILY-WATCH " + str(out)[:80]

def scan_gmail(port):
    hand(port, "navigate", {"url": "https://mail.google.com/mail/u/0/#inbox", "kw": "gmail"})
    time.sleep(6)
    out = hand(port, "eval", {"js": JS_GMAIL_SUBJ, "kw": "gmail"})
    return "SCAN " + str(out)[:250]

def earning_plan(port):
    return "PLAN: Agent School C1 20x999=19980; m1 IN-cta to pending LI leads; m2 WA warm status; m3 voice-agent demo to ecommerce inbox leads."

def audit_check(port):
    out = hand(port, "title", {"kw": "naukri"})
    return "AUDIT " + str(out)[:80]

def ledger_tally(port):
    return "LEDGER-STATE: hunt+triage active; Lok Adalat countdown T-4d (12 Sep)."

def draft_watch(port):
    out = hand(port, "eval", {"js": "() => document.title", "kw": "linkedin"})
    return "DRAFT-SRC " + str(out)[:80]

def relay_check(port):
    out = hand(port, "title", {"kw": "whatsapp"})
    return "RELAY-CHK " + str(out)[:80]


def soldier(tag, sq, cyc, port, kw, duties):
    hb = 0
    while True:
        hb += 1
        try:
            if hb % 4 == 1:
                speak(tag, tag + " alive hb" + str(hb))
                print(tag, "alive", hb)
            if hb % 6 == 3:
                for x in hear(sq):
                    tx = str(x.get("text", ""))
                    if "DUTY:" in tx:
                        print(tag, "ORDERS:", tx[:80])
            if hb % 6 == 1 and (tag.endswith("-01") or hb % 36 == 1):
                for dname, dfn in duties.items():
                    try:
                        out = dfn()
                        if out:
                            print(tag, dname, str(out)[:100])
                            speak(tag, tag + " " + dname + " " + str(out)[:150])
                    except Exception as e:
                        print(tag, dname, "err", str(e)[:60])
        except Exception as e:
            print(tag, "err", str(e)[:50])
        time.sleep(cyc)

grand = 0
for name, port, seat, squads, per, kw in ENGINES:
    duties_for = {
        "SCOUT": {"hunt": lambda: hunt_naukri(port)},
        "DM": {"triage": lambda: triage_linkedin(port)},
        "WA": {"family": lambda: watch_family(port)},
        "WARDEN": {"scan": lambda: scan_gmail(port)},
        "BIZMODEL": {"plan": lambda: earning_plan(port)},
        "MONITOR": {"audit": lambda: audit_check(port)},
        "LEDGER": {"tally": lambda: ledger_tally(port)},
        "COMMENTER": {"draft": lambda: draft_watch(port)},
        "POSTER": {"postdraft": lambda: draft_watch(port)},
        "HERALD": {"relay": lambda: relay_check(port)},
    }
    n = 0
    for sq in squads:
        d = duties_for.get(sq, {"watch": lambda: hand(port, "title", {"kw": kw})})
        for i in range(1, per + 1):
            t = threading.Thread(target=soldier, args=(seat + "-" + sq + "-" + str(i).zfill(2), sq, 30 + i * 3, port, kw, d), daemon=True)
            t.start()
            n += 1
            grand += 1
    speak(seat, seat + " on " + name + ": " + str(n) + " soldiers, hands = FATHERS CHROME")
    print(seat, "on", name, ":", n, "soldiers")
print("ALL ENGINES UP:", grand, "SOLDIERS TOTAL - fathers chrome is the only browser")
speak("ENGINE", "ALL UP: " + str(grand) + " soldiers, hands=fathers chrome")
