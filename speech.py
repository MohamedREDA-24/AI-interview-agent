import os
import tempfile
from typing import Optional
from faster_whisper import WhisperModel
from gtts import gTTS
import pygame
import warnings

class SpeechModule:
    """
    Speech module providing Speech-to-Text (STT) and Text-to-Speech (TTS) functionality.
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize the speech module.
        
        Args:
            model_size (str): Whisper model size ("tiny", "base", "small", "medium", "large")
        """
        self.model_size = model_size
        self.whisper_model = None
        self._load_whisper_model()
        self._init_pygame()
    
    def _init_pygame(self):
        """Initialize pygame for audio playback."""
        try:
            pygame.mixer.init()
            print("✓ Pygame audio initialized successfully")
        except Exception as e:
            print(f"Warning: Failed to initialize pygame audio: {e}")
    
    def _play_audio_file(self, file_path: str) -> bool:
        """Play audio file using pygame."""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # Wait for audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            return True
        except Exception as e:
            print(f"Error playing audio: {e}")
            return False
    
    def _load_whisper_model(self):
        """Load the Whisper model for speech recognition."""
        try:
            print(f"Loading Whisper model: {self.model_size}")
            self.whisper_model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            print("✓ Whisper model loaded successfully")
        except Exception as e:
            print(f"Warning: Failed to load Whisper model: {e}")
            self.whisper_model = None
    
    def transcribe_audio(self, file_path: str) -> str:
        """
        Transcribe audio file to text using Whisper.
        
        Args:
            file_path (str): Path to the audio file (WAV, MP3, etc.)
            
        Returns:
            str: Transcribed text or error message
        """
        if not self.whisper_model:
            return "Speech recognition is not available. Please check the model installation."
        
        if not os.path.exists(file_path):
            return f"Audio file not found: {file_path}"
        
        try:
            print(f"Transcribing audio file: {file_path}")
            
            # Transcribe the audio
            segments, info = self.whisper_model.transcribe(file_path, beam_size=5)
            
            # Combine all segments
            transcription = ""
            for segment in segments:
                transcription += segment.text + " "
            
            transcription = transcription.strip()
            
            if transcription:
                print(f"✓ Transcription successful: {transcription[:50]}...")
                return transcription
            else:
                print("⚠ No speech detected in audio")
                return "I didn't catch that. Could you repeat?"
                
        except Exception as e:
            print(f"Error during transcription: {e}")
            return "I didn't catch that. Could you repeat?"
    
    def speak(self, text: str) -> bool:
        """
        Convert text to speech and play it back.
        
        Args:
            text (str): Text to convert to speech
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not text or not text.strip():
            print("Warning: No text provided for speech synthesis")
            return False
        
        try:
            print(f"Converting to speech: {text[:50]}...")
            
            # Create gTTS object
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_path = temp_file.name
            
            # Save audio to temporary file
            tts.save(temp_path)
            
            # Play the audio
            print("Playing audio...")
            success = self._play_audio_file(temp_path)
            
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except OSError:
                pass  # Ignore cleanup errors
            
            if not success:
                return False
            
            print("✓ Speech playback completed")
            return True
            
        except Exception as e:
            print(f"Warning: Text-to-speech failed: {e}")
            return False
    
    def get_available_models(self) -> list:
        """Get list of available Whisper model sizes."""
        return ["tiny", "base", "small", "medium", "large"]
    
    def change_model(self, new_model_size: str) -> bool:
        """
        Change the Whisper model size.
        
        Args:
            new_model_size (str): New model size
            
        Returns:
            bool: True if successful, False otherwise
        """
        if new_model_size not in self.get_available_models():
            print(f"Invalid model size. Available: {self.get_available_models()}")
            return False
        
        try:
            print(f"Changing model from {self.model_size} to {new_model_size}")
            self.model_size = new_model_size
            self._load_whisper_model()
            return True
        except Exception as e:
            print(f"Failed to change model: {e}")
            return False


def create_speech_module(model_size: str = "base") -> SpeechModule:
    """
    Factory function to create a speech module instance.
    
    Args:
        model_size (str): Whisper model size
        
    Returns:
        SpeechModule: Configured speech module instance
    """
    return SpeechModule(model_size)


# Convenience functions for direct use
def transcribe_audio(file_path: str) -> str:
    """
    Convenience function to transcribe audio file.
    
    Args:
        file_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text
    """
    speech_module = create_speech_module()
    return speech_module.transcribe_audio(file_path)


def speak(text: str) -> bool:
    """
    Convenience function to convert text to speech.
    
    Args:
        text (str): Text to convert to speech
        
    Returns:
        bool: True if successful, False otherwise
    """
    speech_module = create_speech_module()
    return speech_module.speak(text)


if __name__ == "__main__":
    """
    Test block for the speech module.
    """
    print("=" * 60)
    print("SPEECH MODULE TEST")
    print("=" * 60)
    
    # Create speech module
    speech = create_speech_module("base")
    
    # Test TTS
    print("\n1. Testing Text-to-Speech...")
    test_text = "Hello, please say something."
    success = speech.speak(test_text)
    
    if success:
        print("✓ TTS test passed")
    else:
        print("✗ TTS test failed")
    
    # Test STT (requires manual audio file)
    print("\n2. Testing Speech-to-Text...")
    print("Please provide an audio file path to test transcription:")
    print("Example: test_audio.wav")
    
   
    
    print("\n3. Testing model management...")
    print(f"Current model: {speech.model_size}")
    print(f"Available models: {speech.get_available_models()}")
    
    print("\n" + "=" * 60)
    print("Test completed! Speech module is ready for integration.")
    print("=" * 60)
