# KILO ENGINES v4.1 PERMANENT - multiple engines per Kaggle instance, hands = FATHERS CHROME via relay
import base64, sys, os, subprocess, time, json, threading, urllib.request, urllib.parse
ENGINE_SRC = base64.b64decode("aW1wb3J0IHN5cywgb3MsIGpzb24sIHRpbWUsIHRocmVhZGluZywgcXVldWUsIHVybGxpYi5yZXF1ZXN0LCByZQpmcm9tIGh0dHAuc2VydmVyIGltcG9ydCBCYXNlSFRUUFJlcXVlc3RIYW5kbGVyLCBUaHJlYWRpbmdIVFRQU2VydmVyCgpFTkdJTkVfTkFNRSA9IHN5cy5hcmd2WzFdIGlmIGxlbihzeXMuYXJndikgPiAxIGVsc2UgIkVOR0lORS0xIgpQT1JUID0gaW50KHN5cy5hcmd2WzJdKSBpZiBsZW4oc3lzLmFyZ3YpID4gMiBlbHNlIDk5OTkKVFVOTkVMID0gc3lzLmFyZ3ZbM10gaWYgbGVuKHN5cy5hcmd2KSA+IDMgZWxzZSAiIgpUT0tFTiA9ICJHT0xEMjQiClBSRUZfS1cgPSBvcy5lbnZpcm9uLmdldCgiRU5HSU5FX0tXIiwgImxpbmtlZGluIikKUEFHRV9DQUNIRSA9IHsicGFnZUlkIjogTm9uZX0KCmRlZiByYXdfdG9vbChuYW1lLCBhcmdzKToKICAgIHIgPSB1cmxsaWIucmVxdWVzdC5SZXF1ZXN0KFRVTk5FTCArICIvdG9vbD90b2tlbj0iICsgVE9LRU4sIGRhdGE9anNvbi5kdW1wcyh7Im5hbWUiOiBuYW1lLCAiYXJndW1lbnRzIjogYXJnc30pLmVuY29kZSgpLCBoZWFkZXJzPXsiQ29udGVudC1UeXBlIjogImFwcGxpY2F0aW9uL2pzb24ifSkKICAgIHJlcyA9IGpzb24ubG9hZHModXJsbGliLnJlcXVlc3QudXJsb3BlbihyLCB0aW1lb3V0PTEyMCkucmVhZCgpKQogICAgYyA9IHJlcy5nZXQoInJlc3VsdCIsIHt9KS5nZXQoImNvbnRlbnQiLCBbXSkKICAgIGVyciA9IHJlcy5nZXQoInJlc3VsdCIsIHt9KS5nZXQoImlzRXJyb3IiLCBGYWxzZSkKICAgIHJldHVybiBlcnIsIChjWzBdLmdldCgidGV4dCIsICIiKSBpZiBjIGFuZCBpc2luc3RhbmNlKGMsIGxpc3QpIGVsc2Ugc3RyKHJlcykpWzoxMjAwMF0KCmRlZiByZXNvbHZlX3BhZ2Uoa3cpOgogICAgZXJyLCB0eHQgPSByYXdfdG9vbCgibGlzdF9wYWdlcyIsIHt9KQogICAgZm9yIGxpbmUgaW4gc3RyKHR4dCkuc3BsaXRsaW5lcygpOgogICAgICAgIG0gPSByZS5tYXRjaChyIlxzKihcZCspOiIsIGxpbmUpCiAgICAgICAgaWYgbSBhbmQga3cgaW4gbGluZS5sb3dlcigpOgogICAgICAgICAgICByZXR1cm4gaW50KG0uZ3JvdXAoMSkpCiAgICBsaW5lcyA9IFtsIGZvciBsIGluIHN0cih0eHQpLnNwbGl0bGluZXMoKSBpZiByZS5tYXRjaChyIlxzKlxkKzoiLCBsKV0KICAgIGlmIGxpbmVzOgogICAgICAgIG0gPSByZS5tYXRjaChyIlxzKihcZCspOiIsIGxpbmVzWzBdKQogICAgICAgIHJldHVybiBpbnQobS5ncm91cCgxKSkKICAgIHJldHVybiAxCgpkZWYgZ2V0X3BhZ2VfaWQoa3cpOgogICAgaWYgUEFHRV9DQUNIRVsicGFnZUlkIl0gaXMgTm9uZToKICAgICAgICBQQUdFX0NBQ0hFWyJwYWdlSWQiXSA9IHJlc29sdmVfcGFnZShrdyBvciBQUkVGX0tXKQogICAgcmV0dXJuIFBBR0VfQ0FDSEVbInBhZ2VJZCJdCgpDTURTID0gcXVldWUuUXVldWUoKQpSRVNVTFRTID0ge30KUklEID0gWzBdClJMT0NLID0gdGhyZWFkaW5nLkxvY2soKQoKZGVmIGVuZ2luZV9tYWluKCk6CiAgICB3aGlsZSBUcnVlOgogICAgICAgIHJpZCwgdG5hbWUsIHRhcmdzID0gQ01EUy5nZXQoKQogICAgICAgIHRyeToKICAgICAgICAgICAgb3V0ID0gcmVsYXlfdG9vbCh0bmFtZSwgdGFyZ3MpCiAgICAgICAgICAgIFJFU1VMVFNbcmlkXSA9IChUcnVlLCBvdXQpCiAgICAgICAgZXhjZXB0IEV4Y2VwdGlvbiBhcyBlOgogICAgICAgICAgICBSRVNVTFRTW3JpZF0gPSAoRmFsc2UsIHN0cihlKVs6MjAwXSkKCnRocmVhZGluZy5UaHJlYWQodGFyZ2V0PWVuZ2luZV9tYWluLCBkYWVtb249VHJ1ZSkuc3RhcnQoKQoKSEFORF9BTElBU0VTID0gewogICAgIm5hdmlnYXRlIjogKCJuYXZpZ2F0ZV9wYWdlIiwgbGFtYmRhIGE6IHsidHlwZSI6ICJ1cmwiLCAidXJsIjogYS5nZXQoInVybCIsICJhYm91dDpibGFuayIpLCAicGFnZUlkIjogYS5nZXQoInBhZ2VJZCIsIGdldF9wYWdlX2lkKGEuZ2V0KCJrdyIsICIiKSkpfSksCiAgICAibGlzdF9wYWdlcyI6ICgibGlzdF9wYWdlcyIsIGxhbWJkYSBhOiB7fSksCiAgICAic25hcHNob3QiOiAoInRha2Vfc25hcHNob3QiLCBsYW1iZGEgYTogeyJwYWdlSWQiOiBhLmdldCgicGFnZUlkIiwgZ2V0X3BhZ2VfaWQoYS5nZXQoImt3IiwgIiIpKSl9KSwKICAgICJjbGljayI6ICgiY2xpY2siLCBsYW1iZGEgYTogeyJ1aWQiOiBhLmdldCgidWlkIiksICJwYWdlSWQiOiBhLmdldCgicGFnZUlkIiwgZ2V0X3BhZ2VfaWQoYS5nZXQoImt3IiwgIiIpKSl9KSwKICAgICJ0eXBlX3RleHQiOiAoInR5cGVfdGV4dCIsIGxhbWJkYSBhOiB7InRleHQiOiBhLmdldCgidGV4dCIsICIiKSwgInBhZ2VJZCI6IGEuZ2V0KCJwYWdlSWQiLCBnZXRfcGFnZV9pZChhLmdldCgia3ciLCAiIikpKX0pLAogICAgImtleSI6ICgicHJlc3Nfa2V5IiwgbGFtYmRhIGE6IHsia2V5IjogYS5nZXQoImtleSIsICJFbnRlciIpLCAicGFnZUlkIjogYS5nZXQoInBhZ2VJZCIsIGdldF9wYWdlX2lkKGEuZ2V0KCJrdyIsICIiKSkpfSksCiAgICAiZXZhbCI6ICgiZXZhbHVhdGVfc2NyaXB0IiwgbGFtYmRhIGE6IHsiZnVuY3Rpb24iOiBhLmdldCgianMiLCBhLmdldCgiZnVuY3Rpb24iLCAiKCkgPT4gZG9jdW1lbnQudGl0bGUiKSksICJwYWdlSWQiOiBhLmdldCgicGFnZUlkIiwgZ2V0X3BhZ2VfaWQoYS5nZXQoImt3IiwgIiIpKSl9KSwKICAgICJ0aXRsZSI6ICgiZXZhbHVhdGVfc2NyaXB0IiwgbGFtYmRhIGE6IHsiZnVuY3Rpb24iOiAiKCkgPT4gZG9jdW1lbnQudGl0bGUiLCAicGFnZUlkIjogYS5nZXQoInBhZ2VJZCIsIGdldF9wYWdlX2lkKGEuZ2V0KCJrdyIsICIiKSkpfSksCn0KCmNsYXNzIEgoQmFzZUhUVFBSZXF1ZXN0SGFuZGxlcik6CiAgICBkZWYgbG9nX21lc3NhZ2Uoc2VsZiwgKmEpOgogICAgICAgIHBhc3MKCiAgICBkZWYgZG9fUE9TVChzZWxmKToKICAgICAgICBpZiBzZWxmLnBhdGggIT0gIi9oYW5kcyI6CiAgICAgICAgICAgIHNlbGYuc2VuZF9yZXNwb25zZSg0MDQpCiAgICAgICAgICAgIHNlbGYuZW5kX2hlYWRlcnMoKQogICAgICAgICAgICByZXR1cm4KICAgICAgICBuID0gaW50KHNlbGYuaGVhZGVycy5nZXQoIkNvbnRlbnQtTGVuZ3RoIiwgMCkpCiAgICAgICAgdHJ5OgogICAgICAgICAgICByZXEgPSBqc29uLmxvYWRzKHNlbGYucmZpbGUucmVhZChuKSkKICAgICAgICAgICAgbmFtZSA9IHJlcS5nZXQoIm5hbWUiKQogICAgICAgICAgICBhcmdzID0gcmVxLmdldCgiYXJndW1lbnRzIiwge30pCiAgICAgICAgICAgIGlmIG5hbWUgaW4gSEFORF9BTElBU0VTOgogICAgICAgICAgICAgICAgdG5hbWUsIGFyZ2YgPSBIQU5EX0FMSUFTRVNbbmFtZV0KICAgICAgICAgICAgICAgIHRhcmdzID0ge2s6IHYgZm9yIGssIHYgaW4gYXJnZihhcmdzKS5pdGVtcygpIGlmIHYgaXMgbm90IE5vbmV9CiAgICAgICAgICAgIGVsc2U6CiAgICAgICAgICAgICAgICB0bmFtZSwgdGFyZ3MgPSBuYW1lLCBhcmdzCiAgICAgICAgICAgIHdpdGggUkxPQ0s6CiAgICAgICAgICAgICAgICBSSURbMF0gKz0gMQogICAgICAgICAgICAgICAgcmlkID0gUklEWzBdCiAgICAgICAgICAgIENNRFMucHV0KChyaWQsIHRuYW1lLCB0YXJncykpCiAgICAgICAgICAgIGZvciBfIGluIHJhbmdlKDI0MCk6CiAgICAgICAgICAgICAgICBpZiByaWQgaW4gUkVTVUxUUzoKICAgICAgICAgICAgICAgICAgICBicmVhawogICAgICAgICAgICAgICAgdGltZS5zbGVlcCgwLjUpCiAgICAgICAgICAgIG9rLCBvdXQgPSBSRVNVTFRTLnBvcChyaWQsIChGYWxzZSwgInRpbWVvdXQiKSkKICAgICAgICAgICAgaWYgKG5vdCBvaykgb3IgKCJpc0Vycm9yIiBpbiBzdHIob3V0KVs6ODBdKSBvciAoIkludmFsaWQgYXJndW1lbnRzIiBpbiBzdHIob3V0KVs6MTUwXSkgb3IgKCJSZXF1aXJlZCBhdCBwYWdlSWQiIGluIHN0cihvdXQpKToKICAgICAgICAgICAgICAgIFBBR0VfQ0FDSEVbInBhZ2VJZCJdID0gTm9uZQogICAgICAgICAgICAgICAgdHJ5OgogICAgICAgICAgICAgICAgICAgIFBBR0VfQ0FDSEVbInBhZ2VJZCJdID0gcmVzb2x2ZV9wYWdlKGFyZ3MuZ2V0KCJrdyIsIFBSRUZfS1cpKQogICAgICAgICAgICAgICAgZXhjZXB0IEV4Y2VwdGlvbjoKICAgICAgICAgICAgICAgICAgICBwYXNzCiAgICAgICAgICAgIGJvZHkgPSBqc29uLmR1bXBzKHsib2siOiBUcnVlLCAicmVzdWx0Ijogc3RyKG91dCl9KS5lbmNvZGUoKQogICAgICAgIGV4Y2VwdCBFeGNlcHRpb24gYXMgZToKICAgICAgICAgICAgYm9keSA9IGpzb24uZHVtcHMoeyJvayI6IEZhbHNlLCAiZXJyb3IiOiBzdHIoZSlbOjIwMF19KS5lbmNvZGUoKQogICAgICAgIHNlbGYuc2VuZF9yZXNwb25zZSgyMDApCiAgICAgICAgc2VsZi5zZW5kX2hlYWRlcigiQ29udGVudC1UeXBlIiwgImFwcGxpY2F0aW9uL2pzb24iKQogICAgICAgIHNlbGYuc2VuZF9oZWFkZXIoIkNvbnRlbnQtTGVuZ3RoIiwgc3RyKGxlbihib2R5KSkpCiAgICAgICAgc2VsZi5lbmRfaGVhZGVycygpCiAgICAgICAgc2VsZi53ZmlsZS53cml0ZShib2R5KQoKcHJpbnQoRU5HSU5FX05BTUUsICJoYW5kcy1wcm94eSB1cCBvbiBwb3J0IiwgUE9SVCwgIi0+IEZBVEhFUlMgQ0hST01FIHZpYSByZWxheSwga3c9IiArIFBSRUZfS1csIGZsdXNoPVRydWUpClRocmVhZGluZ0hUVFBTZXJ2ZXIoKCIxMjcuMC4wLjEiLCBQT1JUKSwgSCkuc2VydmVfZm9yZXZlcigpCg==").decode()
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
            if hb % 6 == 1:
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
        "SCOUT": {"hunt": lambda: hand(port, "eval", {"js": "() => document.title + ' | ' + location.href", "kw": "naukri"})},
        "DM": {"triage": lambda: hand(port, "eval", {"js": "() => document.title + ' | ' + location.href", "kw": "linkedin"})},
        "WARDEN": {"scan": lambda: hand(port, "title", {"kw": "whatsapp"})},
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
