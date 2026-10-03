lines = open(r'D:\anonym\war-pipe\kilo-core\kernels\kilo-voice-live\kernel.py', encoding='utf-8').readlines()

new_func = (
    "\n"
    "def stream_chunks_long(text, lang, cond_len, max_chars=350):\n"
    "    \"\"\"Split long text into chunks less than max_chars, stream each, yield audio tensors.\"\"\"\n"
    "    import re\n"
    "    sentences = re.split(r'(?<=[.!?।।?!])\\s+', text.strip())\n"
    "    chunks = []\n"
    "    current = ''\n"
    "    for s in sentences:\n"
    "        if len(current) + len(s) + 1 <= max_chars:\n"
    "            current += (' ' if current else '') + s\n"
    "        else:\n"
    "            if current:\n"
    "                chunks.append(current)\n"
    "            current = s\n"
    "    if current:\n"
    "        chunks.append(current)\n"
    "    if not chunks:\n"
    "        chunks = [text[:max_chars]]\n"
    "    prog(f'stream_chunks_long: {len(chunks)} chunks for {len(text)} chars')\n"
    "    for i, chunk in enumerate(chunks):\n"
    "        prog(f'  chunk {i+1}/{len(chunks)}: {len(chunk)} chars')\n"
    "        for audio in m.inference_stream(chunk, lang, gpt_cond_latent=gpt_cond_latent,\n"
    "                                        speaker_embedding=speaker_embedding,\n"
    "                                        temperature=TEMPERATURE):\n"
    "            yield audio\n"
    "\n"
)

lines.insert(186, new_func)
open(r'D:\anonym\war-pipe\kilo-core\kernels\kilo-voice-live\kernel.py', 'w', encoding='utf-8').writelines(lines)
print('INSERTED at line 187')