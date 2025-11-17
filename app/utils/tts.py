import os
import config

# Lazily initialise OpenAI client if available
client = None
if config.OPENAI_API_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
    except Exception:
        client = None


def synthesize_text_to_speech(text, out_path):
    """Synthesize `text` to an audio file at `out_path`.

    Tries OpenAI TTS if available, otherwise returns False.
    Returns True on success, False on failure.
    """
    # Try OpenAI first (if client available and audio.speech API exists)
    if client:
        try:
            # The OpenAI python client may expose a speech create method on client.audio.speech
            # Use a guarded approach so this utility won't crash if the method is missing.
            audio_api = getattr(client, 'audio', None)
            if audio_api and hasattr(audio_api, 'speech'):
                with open(out_path, 'wb') as fout:
                    resp = client.audio.speech.create(
                        model='gpt-4o-mini-tts',
                        voice='alloy',
                        input=text,
                    )
                    # resp might be a bytes-like object or stream; try to write bytes
                    if isinstance(resp, (bytes, bytearray)):
                        fout.write(resp)
                    else:
                        # Fallback: if resp has .read()
                        try:
                            fout.write(resp.read())
                        except Exception:
                            pass
                return os.path.exists(out_path)
        except Exception:
            # fall through to other methods
            pass

    # If OpenAI TTS not available, try gTTS if installed
    try:
        from gtts import gTTS
        tts = gTTS(text)
        tts.save(out_path)
        return True
    except Exception:
        return False
