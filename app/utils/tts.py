import os
import logging
import config

logger = logging.getLogger(__name__)

# Lazily initialise OpenAI client if available
client = None
if config.OPENAI_API_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
    except Exception:
        client = None

# Import offline TTS fallback
from app.utils.offline_tts import synthesize_text_to_speech_offline, is_offline_tts_available


def synthesize_text_to_speech(text, out_path):
    """Synthesize `text` to an audio file at `out_path`.

    Tries OpenAI TTS if available, otherwise returns False.
    Returns True on success, False on failure.
    """
    # Try OpenAI first (if client available and audio.speech API exists)
    if client:
        try:
            # The OpenAI python client exposes client.audio.speech.create for TTS
            audio_api = getattr(client, 'audio', None)
            if audio_api and hasattr(audio_api, 'speech'):
                with open(out_path, 'wb') as fout:
                    resp = client.audio.speech.create(
                        model='tts-1',  # Use tts-1 (fast) or tts-1-hd (high-quality)
                        voice='alloy',  # Options: alloy, echo, fable, onyx, nova, shimmer
                        input=text[:4096],  # Limit to 4096 chars per API limit
                    )
                    # The response has audio bytes accessible via response.content
                    fout.write(resp.content)
                return os.path.exists(out_path) and os.path.getsize(out_path) > 0
        except Exception as e:
            print(f"OpenAI TTS failed: {e}")
            # fall through to other methods
            pass

    # If OpenAI TTS not available, try gTTS if installed
    try:
        from gtts import gTTS
        tts = gTTS(text)
        tts.save(out_path)
        logger.info(f"Generated TTS using gTTS: {out_path}")
        return True
    except Exception:
        pass
    
    # If gTTS not available, try offline TTS using pyttsx3
    if is_offline_tts_available():
        logger.info("Falling back to offline TTS (pyttsx3)")
        return synthesize_text_to_speech_offline(text, out_path)
    
    logger.warning("No TTS method available (OpenAI, gTTS, or pyttsx3)")
    return False
