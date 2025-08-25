#!/usr/bin/env python3
"""
Voice-Based AI Interview Agent - Complete Integration
Integrates STT, TTS, LLM conversation, FAQ system, summarizer, and logging.
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

# Import our modules
from logger import InterviewLogger, generate_session_id
from summarizer import InterviewSummarizer
from faq import FAQModule, is_question_like

# Try to import voice modules
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    print("⚠️  Voice modules not available. Install with: pip install SpeechRecognition pyttsx3")
    VOICE_AVAILABLE = False

# Try to import additional TTS modules
try:
    from gtts import gTTS
    import pygame
    import io
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import win32com.client
    WINDOWS_SAPI_AVAILABLE = True
except ImportError:
    WINDOWS_SAPI_AVAILABLE = False

# Try to import LLM modules
try:
    import google.generativeai as genai
    LLM_AVAILABLE = True
except ImportError:
    print("⚠️  Google Generative AI not available. Install with: pip install google-generativeai")
    LLM_AVAILABLE = False

class VoiceInterviewAgent:
    """
    Complete voice-based AI interview agent with FAQ integration.
    """
    
    def __init__(self):
        """
        Initialize the voice interview agent.
        """
        self.session_id = generate_session_id()
        self.logger = InterviewLogger()
        self.summarizer = InterviewSummarizer()
        self.faq = FAQModule()
        
        # Interview configuration
        self.questions = [
            "What is your full name and background?",
            "Why are you interested in joining the program?",
            "What's your experience with data science or AI?",
            "What are your short-term and long-term goals?",
            "Are you ready to start immediately? If not, when?"
        ]
        
        self.candidate_data = {}
        self.current_question = 0
        
        # Initialize voice components
        if VOICE_AVAILABLE:
            print("🎤 Initializing voice components...")
            self._init_voice()
        else:
            print("❌ Voice modules not available - cannot continue")
            raise Exception("Voice modules not available")
        
        # Initialize LLM if available
        if LLM_AVAILABLE:
            self._init_llm()
    
    def _init_voice(self):
        """Initialize voice recognition and synthesis."""
        try:
            # Speech recognition
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Text-to-speech
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS properties
            self.tts_engine.setProperty('rate', 150)  # Speech rate
            self.tts_engine.setProperty('volume', 1.0)  # Maximum volume
            
            # Try to get available voices and use a good one
            voices = self.tts_engine.getProperty('voices')
            if voices:
                print(f"   Found {len(voices)} voices available")
                # Prefer Microsoft David or Zira for clear speech
                for voice in voices:
                    if any(name in voice.name.lower() for name in ['david', 'zira', 'microsoft']):
                        self.tts_engine.setProperty('voice', voice.id)
                        print(f"   Using voice: {voice.name}")
                        break
            
            # Test audio with a short sound (with timeout protection)
            print("   Testing audio system...")
            try:
                # Try different test messages
                test_messages = ["Audio system ready", "Hello", "Test"]
                for test_msg in test_messages:
                    try:
                        self.tts_engine.say(test_msg)
                        self.tts_engine.runAndWait()
                        print(f"   Audio test completed with: '{test_msg}'")
                        break
                    except Exception as e:
                        print(f"   ⚠️  Test message '{test_msg}' failed: {e}")
                        continue
                else:
                    print("   ⚠️  All audio tests failed, but continuing...")
                    
            except Exception as e:
                print(f"   ⚠️  Audio test failed: {e}")
                print("   Continuing without audio test...")
            
            # Small delay after test
            time.sleep(0.5)
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("✓ Voice components initialized successfully")
            
        except Exception as e:
            print(f"❌ Voice initialization failed: {e}")
            print("   Will try to continue with voice, but some features may not work")
    
    def _init_llm(self):
        """Initialize the LLM for conversation."""
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.llm_model = genai.GenerativeModel('gemini-1.5-flash')
                print("✓ LLM (Gemini) initialized successfully")
            else:
                print("⚠️  GOOGLE_API_KEY not found. LLM conversation disabled.")
                self.llm_model = None
        except Exception as e:
            print(f"❌ LLM initialization failed: {e}")
            self.llm_model = None
    
    def speak(self, text: str):
        """Speak text using TTS - voice only mode with multiple fallbacks."""
        print(f"🎤 Agent: {text}")
        
        # Try multiple TTS methods in order of preference
        tts_methods = [
            ("Windows SAPI", self._speak_windows_sapi),
            ("pyttsx3", self._speak_pyttsx3),
            ("Google TTS", self._speak_gtts)
        ]
        
        for method_name, method_func in tts_methods:
            try:
                print(f"   Trying {method_name}...")
                method_func(text)
                print(f"✓ Speech completed using {method_name}")
                return
            except Exception as e:
                print(f"❌ {method_name} failed: {e}")
                continue
        
        # If all methods fail
        print("🛑 All TTS methods failed - cannot continue without voice")
        raise Exception("All TTS methods failed")
    
    def _speak_windows_sapi(self, text: str):
        """Speak using Windows SAPI (most reliable on Windows)."""
        if not WINDOWS_SAPI_AVAILABLE:
            raise Exception("Windows SAPI not available")
        
        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(text)
        except Exception as e:
            raise Exception(f"Windows SAPI error: {e}")
    
    def _speak_pyttsx3(self, text: str):
        """Speak using pyttsx3."""
        if not VOICE_AVAILABLE:
            raise Exception("pyttsx3 not available")
        
        try:
            # Create new TTS engine
            tts = pyttsx3.init()
            
            # Configure properties
            tts.setProperty('volume', 1.0)
            tts.setProperty('rate', 150)
            
            # Set voice if available
            voices = tts.getProperty('voices')
            if voices:
                for voice in voices:
                    if any(name in voice.name.lower() for name in ['david', 'zira', 'microsoft']):
                        tts.setProperty('voice', voice.id)
                        break
            
            # Speak the text
            tts.say(text)
            tts.runAndWait()
            
            # Clean up
            tts.stop()
            del tts
            
        except Exception as e:
            raise Exception(f"pyttsx3 error: {e}")
    
    def _speak_gtts(self, text: str):
        """Speak using Google Text-to-Speech."""
        if not GTTS_AVAILABLE:
            raise Exception("gTTS not available")
        
        try:
            import tempfile
            import os
            
            # Create TTS object
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                
                # Play the audio file
                pygame.mixer.init()
                pygame.mixer.music.load(tmp_file.name)
                pygame.mixer.music.play()
                
                # Wait for playback to complete
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                pygame.mixer.quit()
                
                # Clean up
                os.unlink(tmp_file.name)
                
        except Exception as e:
            raise Exception(f"gTTS error: {e}")
    
    def listen(self) -> str:
        """Listen for user input using STT - voice only mode."""
        try:
            with self.microphone as source:
                print("🎤 Listening... (speak now)")
                audio = self.recognizer.listen(source, timeout=15, phrase_time_limit=20)
            
            print("🔄 Processing speech...")
            text = self.recognizer.recognize_google(audio)
            print(f"👤 You said: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("⏰ No speech detected within timeout")
            print("🎤 Please speak your answer:")
            return self.listen()  # Retry listening
        except sr.UnknownValueError:
            print("❓ Could not understand speech")
            print("🎤 Please speak more clearly:")
            return self.listen()  # Retry listening
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            print("🎤 Please try speaking again:")
            return self.listen()  # Retry listening
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("🎤 Please try speaking again:")
            return self.listen()  # Retry listening
    
    def get_llm_response(self, user_input: str, context: str = "") -> str:
        """Get response from LLM for conversation."""
        if not self.llm_model:
            return "I'm sorry, the AI conversation system is not available right now."
        
        try:
            prompt = f"""
            You are a professional AI interview assistant. The candidate just said: "{user_input}"
            
            Context: {context}
            
            Provide a brief, professional response. Keep it short and direct.
            If they're asking about the program, give a concise answer.
            Do not provide coaching or suggestions - just answer their question directly.
            
            Response:"""
            
            response = self.llm_model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"❌ LLM error: {e}")
            return "I'm having trouble processing that right now. Could you please continue with your answer?"
    
    def handle_user_input(self, user_input: str) -> str:
        """
        Process user input and return appropriate response.
        Checks FAQ first, then falls back to LLM conversation.
        """
        # Check if input looks like a question
        if is_question_like(user_input):
            print("🔍 Checking FAQ for question...")
            faq_answer = self.faq.get_faq_answer(user_input)
            
            # If FAQ found a good match, use it
            if "I don't have a specific answer" not in faq_answer:
                return f"Great question! {faq_answer}"
        
        # Fall back to LLM conversation
        context = f"Current question: {self.questions[self.current_question]}"
        return self.get_llm_response(user_input, context)
    
    def conduct_interview(self):
        """Conduct the complete voice interview."""
        print("🎯 Starting Voice-Based AI Interview Agent...")
        print("=" * 60)
        
        print("🎤 Voice mode enabled - speak clearly into your microphone")
        if hasattr(self, 'tts_engine') and self.tts_engine:
            print("🔊 Audio system ready - questions will be spoken aloud")
        else:
            print("🛑 Voice system not available - cannot continue without voice")
            raise Exception("Voice system initialization failed")
        
        print(f"📋 Session ID: {self.session_id}")
        print("=" * 60)
        
        # Welcome message
        welcome_msg = "Welcome to the AI Interview Agent! I'll be asking you some questions. Let's begin!"
        print(f"🤖 Agent: {welcome_msg}")
        self.speak(welcome_msg)
        
        # Add a small delay to ensure speech system is ready
        time.sleep(1)
        
        try:
            # Interview loop
            for i, question in enumerate(self.questions):
                self.current_question = i
                question_num = i + 1
                
                print(f"\n📝 Question {question_num}/{len(self.questions)}")
                print("=" * 50)
                print(f"🤖 AGENT ASKING: {question}")
                print("=" * 50)
                
                # Ask the question
                question_msg = f"Question {question_num}: {question}"
                self.speak(question_msg)
                
                # Get user response
                user_answer = ""
                attempts = 0
                max_attempts = 3
                
                while not user_answer.strip() and attempts < max_attempts:
                    attempts += 1
                    if attempts > 1:
                        self.speak(f"Attempt {attempts}. Please try again.")
                    
                    user_answer = self.listen()
                    
                    if not user_answer.strip():
                        if attempts >= max_attempts:
                            self.speak("I'll move to the next question. You can answer this one later if needed.")
                            user_answer = "[No answer provided]"
                            break
                        else:
                            self.speak("I didn't catch that. Could you please repeat your answer?")
                

                
                # Handle if user asks a question instead of answering
                if is_question_like(user_answer):
                    print("🤔 User asked a question instead of answering...")
                    response = self.handle_user_input(user_answer)
                    self.speak(response)
                    
                    # Ask for the actual answer - be direct
                    self.speak("Please answer the interview question now.")
                    user_answer = self.listen()
                
                # Store the answer
                question_key = f"question_{question_num}"
                self.candidate_data[question_key] = {
                    "question": question,
                    "answer": user_answer,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Provide feedback
                feedback_msg = f"Answer recorded for question {question_num}."
                self.speak(feedback_msg)
                
                print(f"✓ Answer recorded for question {question_num}")
                
                # Only ask for questions after the last question
                if question_num < len(self.questions):
                    self.speak("Next question.")
                else:
                    # Allow multiple questions until user says no
                    self.speak("Interview complete. Do you have questions about the program?")
                    
                    while True:
                        user_question = self.listen()
                        
                        # Check if user wants to stop asking questions (improved detection)
                        user_lower = user_question.lower().strip()
                        stop_phrases = ['no', 'nope', 'not really', 'that\'s all', 'no more questions', 
                                      'no thank you', 'no thanks', 'that\'s it', 'i\'m done', 'done', 
                                      'nothing', 'nothing else', 'no more', 'thank you', 'thanks']
                        
                        if not user_question.strip() or any(phrase in user_lower for phrase in stop_phrases):
                            self.speak("Thank you.")
                            break
                        
                        # Handle the question (skip LLM processing, go directly to FAQ or standard response)
                        if is_question_like(user_question):
                            print("🔍 Checking FAQ for question...")
                            faq_answer = self.faq.get_faq_answer(user_question)
                            
                            # If FAQ found a good match, use it
                            if "I don't have a specific answer" not in faq_answer:
                                response = f"Great question! {faq_answer}"
                            else:
                                # Standard professional response for questions not in FAQ
                                response = "For detailed information about that, please visit our website or contact our admissions team directly. They'll be happy to provide you with the most current and comprehensive details."
                        else:
                            response = "Please ask a question about the program."
                        
                        self.speak(response)
                        
                        # Ask if they have more questions
                        self.speak("Do you have any other questions?")
            
            # Interview completed
            self._complete_interview()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Interview interrupted by user")
            self._save_partial_session()
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            self._save_partial_session()
    
    def _complete_interview(self):
        """Complete the interview and generate summary."""
        print("\n" + "=" * 60)
        print("🎉 INTERVIEW COMPLETED!")
        print("=" * 60)
        
        completion_msg = "Generating interview summary."
        self.speak(completion_msg)
        
        # Generate transcript
        transcript = self._generate_transcript()
        
        # Generate AI summary
        print("\n🤖 Generating interview summary...")
        try:
            summary = self.summarizer.summarize_candidate(self.candidate_data)
            print("✓ Summary generated successfully!")
        except Exception as e:
            print(f"⚠️  Warning: Could not generate AI summary: {e}")
            summary = "Summary generation failed. Manual review required."
        
        # Save to database
        print(f"\n💾 Saving interview session: {self.session_id}")
        success = self.logger.save_session(self.session_id, transcript, summary)
        
        if success:
            print("✅ Interview session saved successfully!")
            
            # Display summary
            print("\n📊 INTERVIEW SESSION SUMMARY")
            print("=" * 60)
            print(f"Session ID: {self.session_id}")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total Questions: {len(self.candidate_data)}")
            
            # Parse and display JSON summary
            try:
                summary_data = json.loads(summary)
                print(f"\n📋 AI Summary:")
                print("-" * 40)
                for key, value in summary_data.items():
                    if isinstance(value, list):
                        print(f"{key}: {', '.join(value)}")
                    else:
                        print(f"{key}: {value}")
            except:
                print(f"\n📋 Summary: {summary}")
            
            # Show database stats
            total_sessions = self.logger.get_session_count()
            print(f"\n📈 Database Statistics:")
            print(f"   Total sessions stored: {total_sessions}")
            
        else:
            print("❌ Failed to save interview session!")
        
        print("\n" + "=" * 60)
        print("🎯 Interview session completed!")
        print("=" * 60)
    
    def _generate_transcript(self) -> str:
        """Generate a transcript from the interview data."""
        transcript_lines = []
        transcript_lines.append("VOICE AI INTERVIEW TRANSCRIPT")
        transcript_lines.append("=" * 50)
        transcript_lines.append(f"Session ID: {self.session_id}")
        transcript_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        transcript_lines.append("")
        
        for key, data in sorted(self.candidate_data.items()):
            question_num = key.split('_')[1]
            transcript_lines.append(f"Question {question_num}:")
            transcript_lines.append(f"Q: {data['question']}")
            transcript_lines.append(f"A: {data['answer']}")
            transcript_lines.append(f"Timestamp: {data['timestamp']}")
            transcript_lines.append("")
        
        transcript_lines.append("=" * 50)
        transcript_lines.append("END OF INTERVIEW")
        
        return "\n".join(transcript_lines)
    
    def _save_partial_session(self):
        """Save partial session if interview was interrupted."""
        if self.candidate_data:
            transcript = self._generate_transcript()
            summary = "Interview was interrupted. Partial session data available."
            
            success = self.logger.save_session(self.session_id, transcript, summary)
            if success:
                print(f"💾 Partial session saved: {self.session_id}")
            else:
                print("❌ Failed to save partial session")

def main():
    """Main function to run the voice interview agent."""
    print("🎤 Starting Voice-Only AI Interview Agent...")
    
    try:
        # Create and run the interview agent (voice only)
        agent = VoiceInterviewAgent()
        agent.conduct_interview()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()
