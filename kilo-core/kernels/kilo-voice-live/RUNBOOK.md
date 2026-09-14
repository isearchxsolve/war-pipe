# KILO-VOICE-LIVE — RUNBOOK (family/archive lane, CPML non-commercial)

One call, one session, one kill. The engine pre-warms on Kaggle, waits on the relay, streams Baba's voice home chunk by chunk.

## 1. Go live (Baba, ~3 minutes before the call)

1. Open `kaggle.com/code/kkk3213/kilo-voice-live` (private kernel).
2. Accelerator: **GPU T4 (or T4×2)** — right panel, Settings → Accelerator. Nothing else to set; the gate asserts a T4 and dies cheaply otherwise.
3. Input datasets must be attached (baked into kernel-metadata after first push): `kkk3213/father-xtts`, `kkk3213/father-corpus`, `tinthnhphm21022004/xtts-v2-pretrained`.
4. **Run All.** Watch the log for:
   - `GATE PASS: ['Tesla T4']`
   - `LIVE model loaded`
   - `WARM` ← the readiness line. The engine is now sitting in the polling loop, burning no synthesis GPU.
5. Kaggle sessions die at 9h idle-by-policy anyway; this engine self-kills long before that (below).

Optional tweaks live at the TOP of `kernel.py` (defaults work as-is): `VOICE_REF` (name of a father-corpus window wav — empty = first clean hi row of `metadata_hi.csv`, same idiom as `kilo-xtts-infer`), `LANGUAGE` (default `hi` — DEVA LAW: Bengali goes through Devanagari; `en` for English lines; **`bn` is not an XTTS-v2 lane**), `IDLE_KILL_MIN` (default 10), `POLL_SEC` (default 20), `HARD_CAP_MIN` (quota backstop, default 120).

## 2. Place a call (laptop side, relay = switchboard)

The relay is the door `retrain-schnapps-upbeat.ngrok-free.dev`, token `GOLD24`. Every polling cycle the engine reads its own order-lane via `GET /say?body=LIVE-VOICE`. One call = one order:

```powershell
$json = @{ body = "LIVE-VOICE"; text = 'LIVE_CALL {"cid":"demo1","lang":"hi","text":"फ़ादर, योर सन हियर्स यू।"}' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "https://retrain-schnapps-upbeat.ngrok-free.dev/say?token=GOLD24" -ContentType "application/json" -Body $json
```

- `text` must already be in the deva lane (hi) or English (en) — same transcripts the tune was trained on.
- Multi-sentence answers stream as XTTS chunks: each chunk comes back as base64 WAV in the **KILO order bank**:
  - `LIVE_CHUNK <cid> <chunk#-part#>/<parts>:<base64>` — reassemble parts, decode, play/append in order.
  - `LIVE_DONE <cid> chunks=N first_ms=.. total_ms=..` — the call answer is over.
  - `LIVE_FAIL <cid> <Error>` — engine survived, this call died; place another or check the Kaggle log.
- Consume with `GET /say?token=GOLD24&body=KILO&limit=...` (xtts-player already reads this bank).

End the session on purpose (instead of waiting for idle-kill):

```powershell
$json = @{ body = "LIVE-VOICE"; text = "LIVE_END" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "https://retrain-schnapps-upbeat.ngrok-free.dev/say?token=GOLD24" -ContentType "application/json" -Body $json
```

## 3. How the session dies

- **IDLE_KILL**: no `LIVE_CALL` for `IDLE_KILL_MIN` (10) minutes → `LIVE_BYE IDLE_KILL gpu_s=... calls=...` → clean `sys.exit(0)` → Kaggle session stops, quota stops.
- **LIVE_END**: posted kill-switch, same clean exit.
- **HARD_CAP**: backstop exit at `HARD_CAP_MIN` (120) minutes even if Baba forgets a hot seat.
- Heartbeats: every ~`POLL_SEC × HEARTBEAT_EVERY` (60s) the engine posts `LIVE_BEAT up=..s idle=..s gpu_s=..` so the watchdog/knows the seat is alive; it also prints + logs to `latency_log.jsonl` under `/kaggle/working`.

## 4. Latency numbers

Every run writes `latency_log.jsonl` (chunk gen_ms, cum_ms, first_ms, per-call summary, session gpu_s). The **first_ms** line is the call-feel verdict per LIVE-VOICE-ARCHITECTURE §3 — read it off the kernel output on Kaggle after any real call.

## 5. Fleet discipline

- One kernel = one seat = one attended session. For 3 parallel calls, open the kernel on 3 seats (kkk3213 / n42888 / kdas19999) — give each seat a DIFFERENT `SELF_BODY` or the seats race for the same order.
- Kaggle-first order per standing law; Colab stays batch-only.
- The relay is Baba's laptop — heavy load stays off it: this engine polls the door at most every `POLL_SEC`, and the door's bank write cost is a few KB of JSON.
