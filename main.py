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
from scheduler import MockScheduler

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
        self.scheduler = MockScheduler()
        
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
            print("⏰ I didn't hear anything - no worries!")
            print("🎤 Take your time, I'm listening:")
            return self.listen()  # Retry listening
        except sr.UnknownValueError:
            print("❓ I couldn't quite catch that - happens to the best of us!")
            print("🎤 Could you try speaking a bit more clearly? I'm all ears:")
            return self.listen()  # Retry listening
        except sr.RequestError as e:
            print(f"❌ Having a small technical hiccup: {e}")
            print("🎤 Let's try that again - I'm ready when you are:")
            return self.listen()  # Retry listening
        except Exception as e:
            print(f"❌ Something unexpected happened: {e}")
            print("🎤 No problem, let's give it another shot:")
            return self.listen()  # Retry listening
    
    def get_llm_response(self, user_input: str, context: str = "") -> str:
        """Get response from LLM for conversation."""
        if not self.llm_model:
            return "I'm sorry, the AI conversation system is not available right now."
        
        try:
            prompt = f"""
            You are a warm, friendly AI interview assistant having a natural conversation. The candidate just said: "{user_input}"
            
            Context: {context}
            
            Respond as if you're genuinely excited to get to know this person. Use encouraging language, 
            show authentic interest in their thoughts, and make them feel comfortable and valued.
            If they're asking about the program, answer with enthusiasm and personal touch.
            Remember: this is a conversation between friends, not a formal interview. Answer their question directly.
            
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
    
    def schedule_interview(self) -> Optional[str]:
        """
        Schedule an interview session with the candidate.
        
        Returns:
            str: Session ID if scheduled successfully, None otherwise
        """
        print("\n📅 SCHEDULING INTERVIEW SESSION")
        print("=" * 50)
        
        # Get candidate information via text input
        print("Let's schedule your interview! I'll need some basic information.")
        print()
        
        # Get candidate name
        candidate_name = input("What is your full name? ").strip()
        if not candidate_name:
            candidate_name = "Unknown Candidate"
        
        # Get candidate email
        candidate_email = input("What is your email address? ").strip()
        
        # Get candidate phone
        candidate_phone = input("What is your phone number? ").strip()
        
        # Show available slots
        print("Let me check available interview times.")
        available_slots = self.scheduler.get_available_slots(days_ahead=7)
        
        if not available_slots:
            print("I'm sorry, but there are no available interview slots at the moment. Please try again later.")
            return None
        
        # Present first few available slots
        print(f"I have {len(available_slots)} available interview slots. Here are the next few options:")
        
        for i, slot in enumerate(available_slots[:5], 1):
            slot_time = slot['formatted_time']
            print(f"Option {i}: {slot_time}")
        
        # Ask for preference
        print("Which option would you prefer? Enter the number (1-5):")
        
        user_choice = input("Enter choice: ").strip()
        
        selected_slot = None
        
        try:
            choice_num = int(user_choice)
            if 1 <= choice_num <= 5 and choice_num <= len(available_slots):
                selected_slot = available_slots[choice_num - 1]
            else:
                print("Invalid choice. Selecting the first available slot.")
                selected_slot = available_slots[0]
        except ValueError:
            print("Invalid input. Selecting the first available slot.")
            selected_slot = available_slots[0]
        
        # Book the session
        print(f"Booking your interview for {selected_slot['formatted_time']}.")
        
        session_id = self.scheduler.book_session(
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            candidate_phone=candidate_phone,
            slot_id=selected_slot['slot_id'],
            notes="Scheduled via text interface"
        )
        
        if session_id:
            print(f"Perfect! Your interview is scheduled for {selected_slot['formatted_time']}.")
            print(f"✓ Interview scheduled: {session_id}")
            return session_id
        else:
            print("I'm sorry, there was an issue scheduling your interview. Please try again or contact support.")
            return None
    
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
        welcome_msg = "Hello! I'm excited to chat with you today. I'm here to learn more about you and your interest in our AI program. Think of this as a friendly conversation rather than a formal interview. Ready to get started?"
        print(f"🤖 Agent: {welcome_msg}")
        self.speak(welcome_msg)
        
        # Add a small delay to ensure speech system is ready and create natural pacing
        time.sleep(1.5)
        
        try:
            # Interview loop
            for i, question in enumerate(self.questions):
                self.current_question = i
                question_num = i + 1
                
                print(f"\n📝 Question {question_num}/{len(self.questions)}")
                print("=" * 50)
                
                # Ask the question simply like streamlit
                print(f"🎤 Agent: {question}")
                self.speak(question)
                
                # Get user response
                user_answer = ""
                attempts = 0
                max_attempts = 3
                
                while not user_answer.strip() and attempts < max_attempts:
                    attempts += 1
                    if attempts > 1:
                        encouraging_msgs = [
                            "No worries at all! Take your time and try again.",
                            "That's totally fine! Let's give it another go.",
                            "No problem! I'm here whenever you're ready."
                        ]
                        self.speak(encouraging_msgs[min(attempts-2, len(encouraging_msgs)-1)])
                    
                    user_answer = self.listen()
                    
                    if not user_answer.strip():
                        if attempts >= max_attempts:
                            self.speak("That's okay! Sometimes the audio can be tricky. Let's move forward and we can always come back to this if you'd like.")
                            user_answer = "[Audio difficulties - no answer captured]"
                            break
                        else:
                            self.speak("I'm having trouble hearing you clearly. Could you try once more? I really want to make sure I capture your thoughts properly.")
                

                
                # Handle if user asks a question instead of answering
                if is_question_like(user_answer):
                    print("🤔 User asked a question instead of answering...")
                    response = self.handle_user_input(user_answer)
                    self.speak(response)
                    
                    # Gently redirect to the question
                    redirect_responses = [
                        "That's a great question! I'd love to answer that in a moment. But first, could you help me understand your background?",
                        "I appreciate your curiosity! Let me make sure I get to know you first, then I'll be happy to answer your questions.",
                        "Excellent question! I'll definitely address that. Right now though, I'd love to hear more about your experience."
                    ]
                    redirect_msg = redirect_responses[min(question_num-1, len(redirect_responses)-1)]
                    self.speak(redirect_msg)
                    user_answer = self.listen()
                
                # Store the answer
                question_key = f"question_{question_num}"
                self.candidate_data[question_key] = {
                    "question": question,
                    "answer": user_answer,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Simple acknowledgment like streamlit
                print(f"✓ Answer recorded for question {question_num}")
                
                # Simple transitions like streamlit
                if question_num < len(self.questions):
                    # Just a brief pause, no verbose transitions
                    time.sleep(0.5)
                else:
                    # Simple completion message
                    time.sleep(0.5)
                    self.speak("Thank you! Do you have any questions about the program?")
                    
                    while True:
                        user_question = self.listen()
                        
                        # Check if user wants to stop asking questions (improved detection)
                        user_lower = user_question.lower().strip()
                        stop_phrases = ['no', 'nope', 'not really', 'that\'s all', 'no more questions', 
                                      'no thank you', 'no thanks', 'that\'s it', 'i\'m done', 'done', 
                                      'nothing', 'nothing else', 'no more', 'thank you', 'thanks']
                        
                        if not user_question.strip() or any(phrase in user_lower for phrase in stop_phrases):
                            self.speak("Perfect! It's been such a pleasure talking with you today. Thank you for your time and thoughtful answers!")
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
                        follow_up_msgs = [
                            "What else would you like to know? I'm here for as long as you need!",
                            "Is there anything else I can help clarify? I love answering questions!",
                            "Any other questions on your mind? Don't be shy - ask away!",
                            "What other aspects of the program interest you? I could talk about this all day!",
                            "Anything else you're curious about? I'm really enjoying our conversation!"
                        ]
                        import random
                        # Small pause before asking for more questions
                        time.sleep(0.7)
                        self.speak(random.choice(follow_up_msgs))
            
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
        print("🎉 WHAT A GREAT CONVERSATION!")
        print("=" * 60)
        
        completion_msg = "Thank you so much for that absolutely wonderful conversation! You've been such a pleasure to talk with, and I'm genuinely excited about your potential. I'm just putting together a thoughtful summary of our chat - this will only take a moment, and then you'll be all set!"
        # Pause to let the positive message sink in
        time.sleep(0.8)
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
        print("🎯 It's been wonderful getting to know you!")
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
    """Main function to run the interview agent."""
    print("🎤 Welcome to Your AI Interview Experience!")
    print("=" * 60)
    print("Hey there! 👋 I'm excited to chat with you today.")
    print("What would you like to do?")
    print()
    print("1. 📅 Schedule an interview for later")
    print("2. 🎯 Let's chat right now!")
    print("3. 📊 View my scheduled interviews")
    print("=" * 60)
    
    try:
        # Create the interview agent
        agent = VoiceInterviewAgent()
        
        # Get user choice
        print("Just type 1, 2, or 3 (or say 'schedule', 'chat', 'view'):")
        choice = input("What sounds good? ").strip().lower()
        
        if choice in ['1', 'one', 'schedule', 'scheduling', 'book']:
            print("\n📅 Perfect! Let's get you scheduled...")
            print("This will be quick and easy - just need a few details.")
            session_id = agent.schedule_interview()
            if session_id:
                print(f"\n🎉 Amazing! Your interview is all set!")
                print(f"✅ Confirmation ID: {session_id}")
                print("I can't wait to chat with you!")
            else:
                print("\n😔 Oops! Something went wrong with scheduling.")
                print("Want to try again or chat now instead?")
                
        elif choice in ['2', 'two', 'conduct', 'interview', 'start', 'chat', 'now']:
            print("\n🎯 Fantastic! Let's start our conversation...")
            print("Get comfortable - this is going to be fun!")
            agent.conduct_interview()
            
        elif choice in ['3', 'three', 'view', 'sessions', 'scheduled', 'appointments']:
            print("\n📋 Let me check your scheduled interviews...")
            sessions = agent.scheduler.get_scheduled_sessions()
            if sessions:
                print(f"\n📅 Great! You have {len(sessions)} scheduled interview{'s' if len(sessions) != 1 else ''}:")
                print()
                for i, session in enumerate(sessions, 1):
                    status_emoji = "✅" if session['status'] == 'confirmed' else "🔄" if session['status'] == 'completed' else "❌"
                    print(f"  {i}. {status_emoji} {session['candidate_name']}")
                    print(f"     📅 {session['formatted_time']}")
                    print(f"     📊 Status: {session['status'].title()}")
                    print()
            else:
                print("\n📅 No scheduled interviews yet.")
                print("Would you like to schedule one now? Just run this again and choose option 1!")
                
        else:
            print(f"\nHmm, I didn't quite catch that (you said '{choice}').")
            print("No worries! Let's just start chatting right now - that's the fun part anyway! 🎉")
            agent.conduct_interview()
        
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for stopping by! Hope to chat with you soon!")
    except Exception as e:
        print(f"\n😅 Oops! I ran into a little hiccup: {e}")
        print("Don't worry - these things happen! Try running the program again.")

if __name__ == "__main__":
    main()
