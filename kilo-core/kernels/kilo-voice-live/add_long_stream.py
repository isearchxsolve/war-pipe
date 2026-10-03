def stream_chunks_long(text, lang, cond_len, max_chars=350):
    """Split long text into chunks <= max_chars, stream each, yield audio tensors."""
    import re
    sentences = re.split(r'(?<=[.!?।।?!])\s+', text.strip())
    chunks = []
    current = ''
    for s in sentences:
        if len(current) + len(s) + 1 <= max_chars:
            current += (' ' if current else '') + s
        else:
            if current:
                chunks.append(current)
            current = s
    if current:
        chunks.append(current)
    if not chunks:
        chunks = [text[:max_chars]]
    prog(f'stream_chunks_long: {len(chunks)} chunks for {len(text)} chars')
    for i, chunk in enumerate(chunks):
        prog(f'  chunk {i+1}/{len(chunks)}: {len(chunk)} chars')
        for audio in m.inference_stream(chunk, lang, gpt_cond_latent=gpt_cond_latent,
                                        speaker_embedding=speaker_embedding,
                                        temperature=TEMPERATURE):
            yield audio