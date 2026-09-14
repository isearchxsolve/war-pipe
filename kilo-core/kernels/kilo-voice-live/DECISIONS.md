# KILO-VOICE-LIVE — PARENT DECISIONS (2026-09-13 19:33Z)

Ruling on the builder agent's four open questions. Parent (Kilo) calls; Baba overrides.

1. **POLL_SEC = 20 — BLESSED, keep.** `GET /say` is an in-memory filter on Baba's own relay server-side (no rate limit, son-relay.js:255-260); KiloBridge already holds the same door at 1.5s, so 3 GET/min from a Kaggle seat is noise. Worst case ≈30 GETs/session. Revisit only if ngrok door ever throttles.
2. **Call placement — manual first.** For the measured first calls, POST `LIVE_CALL` via the RUNBOOK §2 PowerShell snippet (or xtts-player's existing send path). Only after `first_ms` is known does wiring move into xtts-player permanently. KiloBridge stays playback-only per its current contract.
3. **Fleet races — single-seat-at-a-time law, for now.** Exactly one seat runs with `SELF_BODY=LIVE-VOICE`; a second seat is never opened while the first is warm. Scale-out rule when needed: seats take `LIVE-VOICE-1/2/3` via the existing `SELF_BODY` over-ride; per-seat inbox naming belongs in relay, not in racing the same bank.
4. **/hear mirroring — deferred, do not code now.** `LIVE_CHUNK` b64 stays sole-dweller of the KILO bank (xtts-player reads it there); `LIVE_DONE`/`LIVE_FAIL`/`LIVE_BYE` are already printed to the Kaggle log, which is the audit trail. Add text-only event mirror to `/hear` only when the order bank measurably crowds.

## Standing reminders (unchanged)
- DEVA LAW stands: `hi` default, `en` passthrough, `bn` normalized to `hi`.
- Ref audio comes from `kkk3213/father-corpus`, not father-xtts (dataset holds weights+config only).
- Dataset push is in flight (father-xtts, 841MB fp16) — kernel push follows PUSH_PLAN.md only after dataset status green.
