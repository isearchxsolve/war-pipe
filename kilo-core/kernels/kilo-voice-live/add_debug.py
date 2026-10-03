lines = open(r'D:\anonym\war-pipe\kilo-core\kernels\kilo-voice-live\kernel.py', encoding='utf-8').readlines()
for i, l in enumerate(lines):
    if 'prog(f"WARM body=' in l:
        print(f'Found at line {i+1}: {l.rstrip()}')
        lines[i] = 'print(f"WARM body={SELF_BODY} poll={POLL_SEC}s", flush=True)\n' + l
        break
open(r'D:\anonym\war-pipe\kilo-core\kernels\kilo-voice-live\kernel.py', 'w', encoding='utf-8').writelines(lines)
print('ADDED STDOUT PRINT')