import config

# Lazily import OpenAI client only when an API key is provided to avoid heavy imports
# and potential import-time errors when running without credentials.
client = None
if config.OPENAI_API_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
    except Exception:
        client = None

def transcribe_audio(audio_file_path):
    if not client or not config.OPENAI_API_KEY:
        raise ValueError("OpenAI API key not configured for transcription")
    
    try:
        with open(audio_file_path, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        text = str(transcription).strip()
        if not text:
            raise ValueError("Transcription returned empty text")
        
        return text
    except Exception as e:
        raise Exception(f"Transcription error: {str(e)}")

def is_audio_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS
