# PUSH PLAN — kilo-voice-live (DO NOT RUN until the father-xtts dataset upload finishes)

A dataset upload (`kkk3213/father-xtts`, 841MB fp16) was in progress in the parent session at the time this kernel was written. Nothing Kaggle-facing was executed here. When the parent confirms the upload landed and is verified:

```powershell
# 0. prereq: dataset present and complete
kaggle datasets status kkk3213/father-xtts

# 1. push the kernel (uses kernel-metadata.json in this folder)
kaggle kernels push -p "D:/anonym/war-pipe/kilo-core/kernels/kilo-voice-live"

# 2. confirm it registered (first run via UI: Baba enables T4 + Run All — the gate asserts)
kaggle kernels status kkk3213/kilo-voice-live

# 3. after a real call, pull the latency ledger for the brief §3 number
kaggle kernels output kkk3213/kilo-voice-live -p "D:/anonym/war-pipe/kilo-core/kernels/kilo-voice-live/out"
```

For the other two fleet seats (kkk3213/n42888/kdas19999), duplicate the kernel on each account (web fork or per-account push) and override `SELF_BODY` per seat — see RUNBOOK §5.

No `dataset push` is needed for this deliverable — `father-xtts` ships from the parent upload; this folder contains only the kernel.
