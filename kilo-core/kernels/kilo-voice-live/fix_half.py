lines = open(r'D:\anonym\war-pipe\kilo-core\kernels\kilo-voice-live\kernel.py', encoding='utf-8').readlines()
# Remove m.half() and update prog message
lines[127] = 'm.cuda()\n'
lines[128] = '# m.half()  # disabled - causes dtype mismatch with inference_stream\n'
lines[129] = 'm.eval()\n'
lines[130] = 'prog("model loaded fp32")\n'
open(r'D:\anonym\war-pipe\kilo-core\kernels\kilo-voice-live\kernel.py', 'w', encoding='utf-8').writelines(lines)
print('FIXED')