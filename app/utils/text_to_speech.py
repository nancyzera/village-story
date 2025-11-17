"""Text-to-Speech utility using OpenAI's TTS API."""
import config
import logging

logger = logging.getLogger(__name__)

client = None
if config.OPENAI_API_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
    except Exception as e:
        logger.warning("Failed to initialize OpenAI client for TTS: %s", e)
        client = None


def text_to_speech(text, audio_file_path, voice='alloy'):
    """Convert text to speech using OpenAI TTS API.
    
    Args:
        text: The text to convert to speech
        audio_file_path: Path where the audio file will be saved
        voice: Voice option ('alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer')
    
    Returns:
        True if successful, False otherwise
    """
    if not client or not config.OPENAI_API_KEY:
        logger.warning("OpenAI API key not configured for text-to-speech")
        return False
    
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text[:4096]  # Limit to 4096 characters per API limit
        )
        
        # Save the audio stream to file
        with open(audio_file_path, 'wb') as f:
            f.write(response.content)
        
        logger.info("Successfully generated TTS audio: %s", audio_file_path)
        return True
    except Exception as e:
        logger.error("Text-to-speech generation failed: %s", e)
        return False


def is_text_to_speech_available():
    """Check if text-to-speech is available (API key configured)."""
    return bool(client and config.OPENAI_API_KEY)
