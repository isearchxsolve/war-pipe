import urllib.request, json, time, re

print("Polling for VOICE_TUNNEL from v80...")
start = time.time()
while time.time() - start < 180:
    try:
        req = urllib.request.Request("http://127.0.0.1:8777/hear?token=GOLD24&limit=10")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            reports = data.get("reports", [])
            for r in reversed(reports):
                text = r.get("text", "")
                if "VOICE_TUNNEL" in text:
                    print("FOUND_TUNNEL:", text)
                    m = re.search(r"https://[^\s]+", text)
                    if m:
                        print("URL:", m.group(0))
                        with open("D:/anonym/war-log/latest_tunnel.txt", "w") as out:
                            out.write(m.group(0))
                    exit(0)
                if "LIVE_READY" in text:
                    print("LIVE_READY:", text)
            if reports:
                print(f"[{int(time.time()-start)}s] Latest report: {reports[-1].get('text')}")
    except Exception as e:
        print("Polling error:", e)
    time.sleep(4)
print("Timeout waiting for tunnel.")
exit(1)
