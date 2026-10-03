lines = open(r'D:\anonym\war-pipe\kilo-core\kernels\kilo-voice-live\kernel.py', encoding='utf-8').readlines()
for i, l in enumerate(lines):
    if 'while True:' in l and i > 270:
        print(f'Found while True at line {i+1}')
        # Add print at start of loop
        lines.insert(i+1, '    print(f"POLL loop iteration {beats+1}", flush=True)\n')
        break
open(r'D:\anonym\war-pipe\kilo-core\kernels\kilo-voice-live\kernel.py', 'w', encoding='utf-8').writelines(lines)
print('ADDED LOOP PRINT')