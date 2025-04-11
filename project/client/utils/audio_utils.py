import io
import base64

def encode_audio_to_base64(audio):
    """Converts an audio file to base64 encoding"""
    buffer = io.BytesIO()
    audio.export(buffer, format="wav")
    audio_bytes = buffer.getvalue()
    return base64.b64encode(audio_bytes).decode()
