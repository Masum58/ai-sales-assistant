import audioop

def pcm_to_mulaw(pcm_data: bytes) -> bytes:
    """
    Convert 16-bit PCM audio to 8-bit mu-law audio.
    Twilio Media Streams expect mu-law 8000Hz.
    """
    return audioop.lin2ulaw(pcm_data, 2)
