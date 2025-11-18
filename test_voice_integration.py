"""Test voice-to-text and text-to-voice integration."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import config
from app.utils.audio_to_text import is_audio_file
from app.utils.tts import synthesize_text_to_speech
from app.utils.text_to_speech import is_text_to_speech_available, text_to_speech
from app.utils.offline_tts import is_offline_tts_available, synthesize_text_to_speech_offline

def main():
    print("=== Voice Integration Test ===\n")
    
    # Check config
    print(f"1. Config Check:")
    print(f"   OPENAI_API_KEY set: {bool(config.OPENAI_API_KEY)}")
    print(f"   UPLOAD_FOLDER: {config.UPLOAD_FOLDER}")
    print(f"   ALLOWED_EXTENSIONS: {config.ALLOWED_EXTENSIONS}\n")
    
    # Test audio file validation
    print(f"2. Audio File Validation:")
    print(f"   is_audio_file('test.mp3'): {is_audio_file('test.mp3')}")
    print(f"   is_audio_file('test.wav'): {is_audio_file('test.wav')}")
    print(f"   is_audio_file('test.txt'): {is_audio_file('test.txt')}\n")
    
    # Test TTS availability
    print(f"3. Text-to-Speech Availability:")
    print(f"   OpenAI TTS available: {is_text_to_speech_available()}")
    print(f"   Offline TTS (pyttsx3) available: {is_offline_tts_available()}\n")
    
    # Test TTS with a sample text
    if config.OPENAI_API_KEY:
        print(f"4. Testing Text-to-Speech Generation (OpenAI):")
        test_text = "Hello, this is a test of the text to speech system."
        test_path = config.UPLOAD_FOLDER / "test_tts.mp3"
        config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        
        try:
            result1 = synthesize_text_to_speech(test_text, str(test_path))
            print(f"   synthesize_text_to_speech() result: {result1}")
            if test_path.exists():
                print(f"   ✓ File created: {test_path.name} ({test_path.stat().st_size} bytes)")
                test_path.unlink()  # Clean up
            else:
                print(f"   ✗ File not created")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test with text_to_speech module
        try:
            result2 = text_to_speech(test_text, str(test_path))
            print(f"   text_to_speech() result: {result2}")
            if test_path.exists():
                print(f"   ✓ File created: {test_path.name} ({test_path.stat().st_size} bytes)")
                test_path.unlink()  # Clean up
            else:
                print(f"   ✗ File not created")
        except Exception as e:
            print(f"   ✗ Error: {e}")
    else:
        print(f"4. Testing Text-to-Speech Generation (OpenAI):")
        print(f"   ✗ OPENAI_API_KEY not set - cannot test\n")
    
    # Test offline TTS
    print(f"5. Testing Offline Text-to-Speech (pyttsx3):")
    test_text = "This is a test of the offline text to speech system."
    test_path = config.UPLOAD_FOLDER / "test_offline_tts.wav"
    config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    
    try:
        result = synthesize_text_to_speech(test_text, str(test_path))
        print(f"   synthesize_text_to_speech() result: {result}")
        if test_path.exists():
            print(f"   ✓ File created: {test_path.name} ({test_path.stat().st_size} bytes)")
        else:
            print(f"   ✗ File not created")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    print()

if __name__ == '__main__':
    main()
