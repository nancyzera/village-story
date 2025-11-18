"""Fallback text-to-speech using pyttsx3 (works offline, no API key needed)."""
import logging

logger = logging.getLogger(__name__)

# Try to import pyttsx3 for offline TTS
pyttsx3_available = False
try:
    import pyttsx3
    pyttsx3_available = True
except ImportError:
    logger.warning("pyttsx3 not installed; fallback TTS won't work. Install with: pip install pyttsx3")


def synthesize_text_to_speech_offline(text, output_path):
    """Generate speech from text using pyttsx3 (offline, no API key needed).
    
    Args:
        text: Text to synthesize
        output_path: Path to save MP3 file
    
    Returns:
        True if successful, False otherwise
    """
    if not pyttsx3_available:
        logger.warning("pyttsx3 not available for offline TTS")
        return False
    
    try:
        engine = pyttsx3.init()
        # Set properties for better quality
        engine.setProperty('rate', 150)  # Speed
        engine.setProperty('volume', 0.9)  # Volume
        
        # Save to file
        engine.save_to_file(text[:1000], output_path)  # Limit text
        engine.runAndWait()
        
        logger.info(f"Generated offline TTS: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Offline TTS generation failed: {e}")
        return False


def is_offline_tts_available():
    """Check if offline TTS (pyttsx3) is available."""
    return pyttsx3_available
