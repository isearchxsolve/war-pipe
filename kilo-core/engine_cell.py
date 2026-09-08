# KILO ENGINE v5 PERMANENT - generic task executor
# New tasks arrive as WIRE ORDERS (TASK:{json}) -> soldiers execute live via hands -> TASK-DONE report.
# No code edits. No restarts. No hand-folding. Ever.
import base64, sys, os, subprocess, time, json, threading, urllib.request, urllib.parse

ENGINE_SRC = base64.b64decode("aW1wb3J0IHN5cywgb3MsIGpzb24sIHRpbWUsIHRocmVhZGluZywgcXVldWUsIHVybGxpYi5yZXF1ZXN0LCByZQpmcm9tIGh0dHAuc2VydmVyIGltcG9ydCBCYXNlSFRUUFJlcXVlc3RIYW5kbGVyLCBUaHJlYWRpbmdIVFRQU2VydmVyCgpFTkdJTkVfTkFNRSA9IHN5cy5hcmd2WzFdIGlmIGxlbihzeXMuYXJndikgPiAxIGVsc2UgIkVOR0lORS0xIgpQT1JUID0gaW50KHN5cy5hcmd2WzJdKSBpZiBsZW4oc3lzLmFyZ3YpID4gMiBlbHNlIDk5OTkKVFVOTkVMID0gc3lzLmFyZ3ZbM10gaWYgbGVuKHN5cy5hcmd2KSA+IDMgZWxzZSAiIgpUT0tFTiA9ICJHT0xEMjQiClBSRUZfS1cgPSBvcy5lbnZpcm9uLmdldCgiRU5HSU5FX0tXIiwgImxpbmtlZGluIikKUEFHRV9DQUNIRSA9IHsicGFnZUlkIjogTm9uZX0KCmRlZiByYXdfdG9vbChuYW1lLCBhcmdzKToKICAgIHIgPSB1cmxsaWIucmVxdWVzdC5SZXF1ZXN0KFRVTk5FTCArICIvdG9vbD90b2tlbj0iICsgVE9LRU4sIGRhdGE9anNvbi5kdW1wcyh7Im5hbWUiOiBuYW1lLCAiYXJndW1lbnRzIjogYXJnc30pLmVuY29kZSgpLCBoZWFkZXJzPXsiQ29udGVudC1UeXBlIjogImFwcGxpY2F0aW9uL2pzb24ifSkKICAgIHJlcyA9IGpzb24ubG9hZHModXJsbGliLnJlcXVlc3QudXJsb3BlbihyLCB0aW1lb3V0PTEyMCkucmVhZCgpKQogICAgYyA9IHJlcy5nZXQoInJlc3VsdCIsIHt9KS5nZXQoImNvbnRlbnQiLCBbXSkKICAgIGVyciA9IHJlcy5nZXQoInJlc3VsdCIsIHt9KS5nZXQoImlzRXJyb3IiLCBGYWxzZSkKICAgIHJldHVybiBlcnIsIChjWzBdLmdldCgidGV4dCIsICIiKSBpZiBjIGFuZCBpc2luc3RhbmNlKGMsIGxpc3QpIGVsc2Ugc3RyKHJlcykpWzoxMjAwMF0KCmRlZiByZXNvbHZlX3BhZ2Uoa3cpOgogICAgZXJyLCB0eHQgPSByYXdfdG9vbCgibGlzdF9wYWdlcyIsIHt9KQogICAgZm9yIGxpbmUgaW4gc3RyKHR4dCkuc3BsaXRsaW5lcygpOgogICAgICAgIG0gPSByZS5tYXRjaChyIlxzKihcZCspOiIsIGxpbmUpCiAgICAgICAgaWYgbSBhbmQga3cgaW4gbGluZS5sb3dlcigpOgogICAgICAgICAgICByZXR1cm4gaW50KG0uZ3JvdXAoMSkpCiAgICBsaW5lcyA9IFtsIGZvciBsIGluIHN0cih0eHQpLnNwbGl0bGluZXMoKSBpZiByZS5tYXRjaChyIlxzKlxkKzoiLCBsKV0KICAgIGlmIGxpbmVzOgogICAgICAgIHJldHVybiBpbnQocmUubWF0Y2gociJccyooXGQrKToiLCBsaW5lc1swXSkuZ3JvdXAoMSkpCiAgICByZXR1cm4gMQoKZGVmIGdldF9wYWdlX2lkKGt3KToKICAgIGlmIFBBR0VfQ0FDSEVbInBhZ2VJZCJdIGlzIE5vbmU6CiAgICAgICAgUEFHRV9DQUNIRVsicGFnZUlkIl0gPSByZXNvbHZlX3BhZ2Uoa3cgb3IgUFJFRl9LVykKICAgIHJldHVybiBQQUdFX0NBQ0hFWyJwYWdlSWQiXQoKQ01EUyA9IHF1ZXVlLlF1ZXVlKCkKUkVTVUxUUyA9IHt9ClJJRCA9IFswXQpSTE9DSyA9IHRocmVhZGluZy5Mb2NrKCkKCmRlZiBlbmdpbmVfbWFpbigpOgogICAgd2hpbGUgVHJ1ZToKICAgICAgICByaWQsIHRuYW1lLCB0YXJncyA9IENNRFMuZ2V0KCkKICAgICAgICB0cnk6CiAgICAgICAgICAgIG91dCA9IHJhd190b29sKHRuYW1lLCB0YXJncykKICAgICAgICAgICAgUkVTVUxUU1tyaWRdID0gKFRydWUsIG91dCkKICAgICAgICBleGNlcHQgRXhjZXB0aW9uIGFzIGU6CiAgICAgICAgICAgIFJFU1VMVFNbcmlkXSA9IChGYWxzZSwgc3RyKGUpWzoyMDBdKQoKdGhyZWFkaW5nLlRocmVhZCh0YXJnZXQ9ZW5naW5lX21haW4sIGRhZW1vbj1UcnVlKS5zdGFydCgpCgpIQU5EX0FMSUFTRVMgPSB7CiAgICAibmF2aWdhdGUiOiAoIm5hdmlnYXRlX3BhZ2UiLCBsYW1iZGEgYTogeyJ0eXBlIjogInVybCIsICJ1cmwiOiBhLmdldCgidXJsIiwgImFib3V0OmJsYW5rIiksICJwYWdlSWQiOiBhLmdldCgicGFnZUlkIiwgZ2V0X3BhZ2VfaWQoYS5nZXQoImt3IiwgIiIpKSl9KSwKICAgICJsaXN0X3BhZ2VzIjogKCJsaXN0X3BhZ2VzIiwgbGFtYmRhIGE6IHt9KSwKICAgICJzbmFwc2hvdCI6ICgidGFrZV9zbmFwc2hvdCIsIGxhbWJkYSBhOiB7InBhZ2VJZCI6IGEuZ2V0KCJwYWdlSWQiLCBnZXRfcGFnZV9pZChhLmdldCgia3ciLCAiIikpKX0pLAogICAgImNsaWNrIjogKCJjbGljayIsIGxhbWJkYSBhOiB7InVpZCI6IGEuZ2V0KCJ1aWQiKSwgInBhZ2VJZCI6IGEuZ2V0KCJwYWdlSWQiLCBnZXRfcGFnZV9pZChhLmdldCgia3ciLCAiIikpKX0pLAogICAgInR5cGVfdGV4dCI6ICgidHlwZV90ZXh0IiwgbGFtYmRhIGE6IHsidGV4dCI6IGEuZ2V0KCJ0ZXh0IiwgIiIpLCAicGFnZUlkIjogYS5nZXQoInBhZ2VJZCIsIGdldF9wYWdlX2lkKGEuZ2V0KCJrdyIsICIiKSkpfSksCiAgICAia2V5IjogKCJwcmVzc19rZXkiLCBsYW1iZGEgYTogeyJrZXkiOiBhLmdldCgia2V5IiwgIkVudGVyIiksICJwYWdlSWQiOiBhLmdldCgicGFnZUlkIiwgZ2V0X3BhZ2VfaWQoYS5nZXQoImt3IiwgIiIpKSl9KSwKICAgICJldmFsIjogKCJldmFsdWF0ZV9zY3JpcHQiLCBsYW1iZGEgYTogeyJmdW5jdGlvbiI6IGEuZ2V0KCJqcyIsIGEuZ2V0KCJmdW5jdGlvbiIsICIoKSA9PiBkb2N1bWVudC50aXRsZSIpKSwgInBhZ2VJZCI6IGEuZ2V0KCJwYWdlSWQiLCBnZXRfcGFnZV9pZChhLmdldCgia3ciLCAiIikpKX0pLAogICAgInRpdGxlIjogKCJldmFsdWF0ZV9zY3JpcHQiLCBsYW1iZGEgYTogeyJmdW5jdGlvbiI6ICIoKSA9PiBkb2N1bWVudC50aXRsZSIsICJwYWdlSWQiOiBhLmdldCgicGFnZUlkIiwgZ2V0X3BhZ2VfaWQoYS5nZXQoImt3IiwgIiIpKSl9KSwKfQoKY2xhc3MgSChCYXNlSFRUUFJlcXVlc3RIYW5kbGVyKToKICAgIGRlZiBsb2dfbWVzc2FnZShzZWxmLCAqYSk6CiAgICAgICAgcGFzcwoKICAgIGRlZiBkb19QT1NUKHNlbGYpOgogICAgICAgIGlmIHNlbGYucGF0aCAhPSAiL2hhbmRzIjoKICAgICAgICAgICAgc2VsZi5zZW5kX3Jlc3BvbnNlKDQwNCkKICAgICAgICAgICAgc2VsZi5lbmRfaGVhZGVycygpCiAgICAgICAgICAgIHJldHVybgogICAgICAgIG4gPSBpbnQoc2VsZi5oZWFkZXJzLmdldCgiQ29udGVudC1MZW5ndGgiLCAwKSkKICAgICAgICB0cnk6CiAgICAgICAgICAgIHJlcSA9IGpzb24ubG9hZHMoc2VsZi5yZmlsZS5yZWFkKG4pKQogICAgICAgICAgICBuYW1lID0gcmVxLmdldCgibmFtZSIpCiAgICAgICAgICAgIGFyZ3MgPSByZXEuZ2V0KCJhcmd1bWVudHMiLCB7fSkKICAgICAgICAgICAgaWYgbmFtZSBpbiBIQU5EX0FMSUFTRVM6CiAgICAgICAgICAgICAgICB0bmFtZSwgYXJnZiA9IEhBTkRfQUxJQVNFU1tuYW1lXQogICAgICAgICAgICAgICAgdGFyZ3MgPSB7azogdiBmb3IgaywgdiBpbiBhcmdmKGFyZ3MpLml0ZW1zKCkgaWYgdiBpcyBub3QgTm9uZX0KICAgICAgICAgICAgZWxzZToKICAgICAgICAgICAgICAgIHRuYW1lLCB0YXJncyA9IG5hbWUsIGFyZ3MKICAgICAgICAgICAgd2l0aCBSTE9DSzoKICAgICAgICAgICAgICAgIFJJRFswXSArPSAxCiAgICAgICAgICAgICAgICByaWQgPSBSSURbMF0KICAgICAgICAgICAgQ01EUy5wdXQoKHJpZCwgdG5hbWUsIHRhcmdzKSkKICAgICAgICAgICAgZm9yIF8gaW4gcmFuZ2UoMjQwKToKICAgICAgICAgICAgICAgIGlmIHJpZCBpbiBSRVNVTFRTOgogICAgICAgICAgICAgICAgICAgIGJyZWFrCiAgICAgICAgICAgICAgICB0aW1lLnNsZWVwKDAuNSkKICAgICAgICAgICAgb2ssIG91dCA9IFJFU1VMVFMucG9wKHJpZCwgKEZhbHNlLCAidGltZW91dCIpKQogICAgICAgICAgICBpZiAobm90IG9rKSBvciAoIkludmFsaWQgYXJndW1lbnRzIiBpbiBzdHIob3V0KVs6MTUwXSkgb3IgKCJSZXF1aXJlZCBhdCBwYWdlSWQiIGluIHN0cihvdXQpKToKICAgICAgICAgICAgICAgIFBBR0VfQ0FDSEVbInBhZ2VJZCJdID0gTm9uZQogICAgICAgICAgICBib2R5ID0ganNvbi5kdW1wcyh7Im9rIjogVHJ1ZSwgInJlc3VsdCI6IHN0cihvdXQpfSkuZW5jb2RlKCkKICAgICAgICBleGNlcHQgRXhjZXB0aW9uIGFzIGU6CiAgICAgICAgICAgIGJvZHkgPSBqc29uLmR1bXBzKHsib2siOiBGYWxzZSwgImVycm9yIjogc3RyKGUpWzoyMDBdfSkuZW5jb2RlKCkKICAgICAgICBzZWxmLnNlbmRfcmVzcG9uc2UoMjAwKQogICAgICAgIHNlbGYuc2VuZF9oZWFkZXIoIkNvbnRlbnQtVHlwZSIsICJhcHBsaWNhdGlvbi9qc29uIikKICAgICAgICBzZWxmLnNlbmRfaGVhZGVyKCJDb250ZW50LUxlbmd0aCIsIHN0cihsZW4oYm9keSkpKQogICAgICAgIHNlbGYuZW5kX2hlYWRlcnMoKQogICAgICAgIHNlbGYud2ZpbGUud3JpdGUoYm9keSkKCnByaW50KEVOR0lORV9OQU1FLCAiaGFuZHMtcHJveHkgdXAgcG9ydCIsIFBPUlQsICItPiBGQVRIRVJTIENIUk9NRSB2aWEgcmVsYXkiLCBmbHVzaD1UcnVlKQpUaHJlYWRpbmdIVFRQU2VydmVyKCgiMTI3LjAuMC4xIiwgUE9SVCksIEgpLnNlcnZlX2ZvcmV2ZXIoKQo=").decode()
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
for name, port, seat, squads, per, kw in ENGINES:
    env = dict(os.environ)
    env["ENGINE_KW"] = kw
    subprocess.Popen([sys.executable, "/kaggle/working/kilo_engine_server.py", name, str(port), TUNNEL], env=env)
print("engines spawning...")
time.sleep(12)

DONE = set()

def execute_task(tag, port, kw, task):
    steps = task.get("steps", [])
    for i, st in enumerate(steps):
        try:
            a = dict(st.get("args", {}))
            a["kw"] = kw
            out = hand(port, st.get("hand", "eval"), a)
            print(tag, "step", i, str(out)[:90])
        except Exception as e:
            speak(tag, "TASK-FAIL " + str(task.get("name", "?")) + " step " + str(i) + ": " + str(e)[:80])
            return
    speak(tag, "TASK-DONE " + str(task.get("name", "?")) + " " + str(task.get("report", ""))[:120])

def soldier(tag, sq, cyc, port, kw):
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
                    if tx.startswith("TASK:"):
                        try:
                            task = json.loads(tx[5:])
                            tname = "T" + str(task.get("name", "?")) + str(task.get("issued", ""))
                            if tname not in DONE:
                                DONE.add(tname)
                                speak(tag, "TASK-START " + str(task.get("name", "?")))
                                execute_task(tag, port, kw, task)
                        except Exception as e:
                            print(tag, "task-parse err", str(e)[:60])
            if hb % 12 == 6:
                try:
                    out = hand(port, "eval", {"js": "() => document.title", "kw": kw})
                    print(tag, "eyes:", str(out)[:80])
                except Exception as e:
                    print(tag, "eyes err", str(e)[:40])
        except Exception as e:
            print(tag, "err", str(e)[:50])
        time.sleep(cyc)

grand = 0
for name, port, seat, squads, per, kw in ENGINES:
    n = 0
    for sq in squads:
        for i in range(1, per + 1):
            t = threading.Thread(target=soldier, args=(seat + "-" + sq + "-" + str(i).zfill(2), sq, 30 + i * 3, port, kw), daemon=True)
            t.start()
            n += 1
            grand += 1
    speak(seat, seat + " on " + name + ": " + str(n) + " soldiers, generic task executor LIVE")
    print(seat, "on", name, ":", n)
print("ALL ENGINES UP:", grand, "- v5: tasks arrive as orders, executed live, no restarts")
speak("ENGINE", "v5 UP: " + str(grand) + " soldiers, generic executor live")
