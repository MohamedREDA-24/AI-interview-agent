#!/usr/bin/env python3
"""
Streamlit UI for AI Interview Agent
"""

import streamlit as st
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd

# Import our modules
from scheduler import MockScheduler
from faq import FAQModule, is_question_like
from logger import InterviewLogger, generate_session_id
from summarizer import InterviewSummarizer

# Voice modules with lazy loading
VOICE_AVAILABLE = False
_voice_modules = {}

def load_voice_modules():
    """Lazy load voice modules only when needed."""
    global VOICE_AVAILABLE, _voice_modules
    if not _voice_modules:
        try:
            import speech_recognition as sr
            import pyttsx3
            from gtts import gTTS
            import pygame
            _voice_modules = {'sr': sr, 'pyttsx3': pyttsx3, 'gTTS': gTTS, 'pygame': pygame}
            VOICE_AVAILABLE = True
        except ImportError:
            VOICE_AVAILABLE = False
    return VOICE_AVAILABLE

# Page configuration
st.set_page_config(
    page_title="AI Interview Agent",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS
st.markdown("""
<style>
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables efficiently."""
    defaults = {
        'current_page': 'Home',
        'current_question': 0,
        'candidate_data': {},
        'session_id': None,
        'interview_started': False,
        'is_listening': False,
        'question_spoken': {},
        'auto_summary_generated': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Initialize voice components only when needed
    if load_voice_modules() and 'recognizer' not in st.session_state:
        sr = _voice_modules['sr']
        st.session_state.recognizer = sr.Recognizer()
        st.session_state.microphone = sr.Microphone()

def sidebar_navigation():
    """Create sidebar navigation."""
    st.sidebar.title("🎤 Interview Agent")
    st.sidebar.markdown("---")
    
    pages = {
        "🏠 Home": "Home",
        "🎯 Interview": "Interview",
        "📅 Schedule": "Scheduling", 
        "📊 Sessions": "Sessions"
    }
    
    for display_name, page_name in pages.items():
        if st.sidebar.button(display_name, use_container_width=True):
            st.session_state.current_page = page_name
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Cached session count
    if 'session_count' not in st.session_state:
        try:
            logger = InterviewLogger()
            st.session_state.session_count = logger.get_session_count()
        except:
            st.session_state.session_count = 0
    
    st.sidebar.metric("Sessions", st.session_state.session_count)

def home_page():
    """Home page with project overview."""
    st.title("🎤 Welcome to Your AI Interview Experience!")
    st.markdown("### Let's have a friendly conversation about your future")
    
    # Warm welcome message
    st.markdown("""
    Hi there! 👋 I'm so excited you're here. This isn't your typical stiff interview - 
    think of it more like chatting with a friend who's genuinely interested in getting to know you.
    
    **Here's what we can do together:**
    - 🗣️ Have a natural voice conversation (just like talking to a person!)
    - 🤖 Get instant answers to all your questions about our program
    - 📅 Schedule a time that works perfectly for you
    - 📊 Keep track of our conversations for future reference
    
    Ready to get started? I can't wait to learn more about you!
    """)
    
    # Quick navigation
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎯 Let's Chat Now!", use_container_width=True):
            st.session_state.current_page = "Interview"
            st.rerun()
    
    with col2:
        if st.button("📅 Pick a Time", use_container_width=True):
            st.session_state.current_page = "Scheduling"
            st.rerun()
    
    with col3:
        if st.button("📊 My Conversations", use_container_width=True):
            st.session_state.current_page = "Sessions"
            st.rerun()

def reset_interview_state():
    """Efficiently reset interview state."""
    reset_values = {
        'current_question': 0,
        'candidate_data': {},
        'session_id': None,
        'interview_started': False,
        'is_listening': False,
        'question_spoken': {},
        'auto_summary_generated': False
    }
    
    # Reset core values
    for key, value in reset_values.items():
        st.session_state[key] = value
    
    # Remove temporary keys
    temp_keys = ['show_faq', 'current_voice_question', 'post_interview_questions', 'faq_prompt_spoken']
    for key in temp_keys:
        st.session_state.pop(key, None)

@st.cache_data
def get_interview_questions():
    """Cache interview questions."""
    return [
        "What is your full name and background?",
        "Why are you interested in joining the program?",
        "What's your experience with data science or AI?",
        "What are your short-term and long-term goals?",
        "Are you ready to start immediately? If not, when?"
    ]

@st.cache_resource
def get_tts_engine():
    """Get cached TTS engine with optimized settings."""
    if not load_voice_modules():
        return None
    
    try:
        pyttsx3 = _voice_modules['pyttsx3']
        engine = pyttsx3.init()
        
        # Optimize settings for clarity
        engine.setProperty('rate', 140)  # Slightly slower
        engine.setProperty('volume', 1.0)  # Full volume
        
        # Try to use a better voice
        voices = engine.getProperty('voices')
        if voices and len(voices) > 1:
            # Prefer the second voice if available (often better quality)
            engine.setProperty('voice', voices[1].id)
        
        return engine
    except:
        return None

def speak_text(text: str):
    """Improved text-to-speech with better audio quality."""
    if not load_voice_modules():
        return
    
    try:
        # Try Windows SAPI first (best quality on Windows)
        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            # Set voice properties for better clarity
            voices = speaker.GetVoices()
            if voices.Count > 0:
                speaker.Voice = voices.Item(0)  # Use first available voice
            speaker.Rate = 0  # Normal speed
            speaker.Volume = 100  # Full volume
            speaker.Speak(text)
            return
        except:
            pass
        
        # Try pyttsx3 with improved settings
        engine = get_tts_engine()
        if engine:
            # Improve audio quality settings
            engine.setProperty('rate', 140)  # Slightly slower for clarity
            engine.setProperty('volume', 1.0)  # Full volume
            
            # Try to set a better voice if available
            voices = engine.getProperty('voices')
            if voices:
                # Prefer female voices or higher quality voices
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            
            engine.say(text)
            engine.runAndWait()
            return
        
        # Fallback to gTTS with improved settings
        gTTS = _voice_modules['gTTS']
        pygame = _voice_modules['pygame']
        
        # Use slower speech for better clarity
        tts = gTTS(text=text, lang='en', slow=False)
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            
            # Initialize pygame mixer with better quality settings
            pygame.mixer.quit()  # Ensure clean state
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.music.load(tmp_file.name)
            pygame.mixer.music.set_volume(1.0)  # Full volume
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                pygame.time.wait(50)  # Shorter wait for responsiveness
            
            # Clean up
            pygame.mixer.music.stop()
            pygame.time.wait(100)  # Brief pause before cleanup
            os.unlink(tmp_file.name)
            
    except Exception as e:
        # Silently fail to avoid disrupting the interview
        print(f"TTS Error: {e}")

def listen_for_speech() -> Optional[str]:
    """Optimized speech recognition."""
    if not load_voice_modules():
        return None
    
    try:
        sr = _voice_modules['sr']
        
        # Use cached recognizer or create new one
        if 'recognizer' not in st.session_state:
            st.session_state.recognizer = sr.Recognizer()
            st.session_state.microphone = sr.Microphone()
        
        recognizer = st.session_state.recognizer
        microphone = st.session_state.microphone
        
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=20)
        
        try:
            return recognizer.recognize_google(audio)
        except (sr.UnknownValueError, sr.RequestError):
            return None
            
    except Exception:
        return None
    except sr.RequestError as e:
        st.error(f"❌ Speech recognition error: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        return None

@st.cache_resource
def get_faq_module():
    """Get cached FAQ module."""
    return FAQModule()

@st.cache_resource  
def get_scheduler():
    """Get cached scheduler."""
    return MockScheduler()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def handle_user_input(user_input: str) -> str:
    """Optimized user input handling."""
    try:
        faq_module = get_faq_module()
        
        if is_question_like(user_input):
            faq_answer = faq_module.get_faq_answer(user_input)
            if faq_answer and "I don't have information" not in faq_answer:
                return faq_answer
        
        return f"Thank you for your question. Our team will provide detailed information about '{user_input[:50]}...'."
        
    except Exception:
        return "I'm having trouble processing your question. Please try again."

def interview_page():
    """Main interview interface."""
    st.title("🎯 Let's Get to Know Each Other!")
    
    questions = get_interview_questions()
    
    # Initialize session
    if not st.session_state.session_id:
        st.session_state.session_id = generate_session_id()
    
    st.info(f"💬 **Our Conversation ID:** {st.session_state.session_id} (just for our records!)")
    
    # Simple progress indicator
    if st.session_state.current_question < len(questions):
        progress = (st.session_state.current_question) / len(questions)
        st.progress(progress)
    
    # Interview interface
    if st.session_state.current_question < len(questions):
        current_q = st.session_state.current_question
        question = questions[current_q]
        
        st.markdown(f"### Let's talk about... (Question {current_q + 1} of {len(questions)})")
        st.markdown(f"**{question}**")
        st.markdown("*Take your time - I'm genuinely curious to hear your thoughts!*")
        
        # Auto-speak question if not already spoken
        if load_voice_modules() and not st.session_state.question_spoken.get(current_q, False):
            # Add a small delay to ensure UI is ready
            import time
            time.sleep(0.5)
            speak_text(question)
            st.session_state.question_spoken[current_q] = True
        
        # Voice + Text interface
        voice_text_interface(question, current_q)
    
    else:
        # Interview completed - now allow questions
        st.success("🎉 What a wonderful conversation! Thank you for sharing so much with me.")
        
        # FAQ Section after interview completion
        st.markdown("---")
        st.markdown("### ❓ Now it's your turn - what would you like to know?")
        st.markdown("*I'm here to answer anything about our program. No question is too small!*")
        
        # Auto-speak FAQ prompt if not already spoken
        if load_voice_modules() and not st.session_state.get('faq_prompt_spoken', False):
            import time
            time.sleep(0.5)
            speak_text("That was such a great conversation! Now I'd love to answer any questions you have about our program. What would you like to know?")
            st.session_state.faq_prompt_spoken = True
        
        # Question input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            user_question = st.text_input(
                "What's on your mind?",
                value=st.session_state.get('current_voice_question', ''),
                key="post_interview_question",
                placeholder="Ask me anything about the program - I love questions!"
            )
        
        with col2:
            if load_voice_modules() and st.button("🎤", key="voice_question"):
                with st.spinner("Listening..."):
                    voice_question = listen_for_speech()
                    if voice_question:
                        st.session_state.current_voice_question = voice_question
                        st.rerun()
        
        # Process question
        if user_question and st.button("Tell me more! 💭", key="get_answer_post"):
            with st.spinner("Processing..."):
                try:
                    response = handle_user_input(user_question)
                    st.markdown(f"💬 **{response}**")
                    
                    # Auto-speak the answer
                    if load_voice_modules():
                        speak_text(response)
                    
                    # Store the Q&A
                    if 'post_interview_questions' not in st.session_state:
                        st.session_state.post_interview_questions = []
                    st.session_state.post_interview_questions.append({
                        "question": user_question,
                        "answer": response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    if 'current_voice_question' in st.session_state:
                        del st.session_state.current_voice_question
                    
                except Exception as e:
                    st.error(f"Oops! I had a little hiccup there: {e}. Could you try asking again?")
        
        # Previous Q&As (simplified)
        if hasattr(st.session_state, 'post_interview_questions') and st.session_state.post_interview_questions:
            st.markdown("---")
            for qa in st.session_state.post_interview_questions[-3:]:  # Show only last 3
                st.markdown(f"**Q:** {qa['question']}")
                st.markdown(f"**A:** {qa['answer']}")
                st.markdown("")
        
        # Auto-generate summary immediately when interview ends
        if not st.session_state.auto_summary_generated:
            with st.spinner("Saving interview..."):
                try:
                    summarizer = InterviewSummarizer()
                    summary_json = summarizer.summarize_candidate(st.session_state.candidate_data)
                    
                    logger = InterviewLogger()
                    transcript = generate_transcript(st.session_state.candidate_data, st.session_state.session_id)
                    
                    if hasattr(st.session_state, 'post_interview_questions'):
                        transcript += "\n\n=== POST-INTERVIEW QUESTIONS ===\n"
                        for i, qa in enumerate(st.session_state.post_interview_questions, 1):
                            transcript += f"\nQ{i}: {qa['question']}\n"
                            transcript += f"A{i}: {qa['answer']}\n"
                    
                    success = logger.save_session(st.session_state.session_id, transcript, summary_json)
                    
                    if success:
                        st.session_state.auto_summary_generated = True
                        # Update session count cache
                        st.session_state.session_count = st.session_state.get('session_count', 0) + 1
                        
                        st.success("✅ Perfect! Our conversation is safely saved. You were amazing to talk with!")
                    else:
                        st.error("Oops! I had trouble saving our conversation, but don't worry - we can try again!")
                        
                except Exception as e:
                    st.error(f"I ran into a small issue creating your summary: {e}. But our conversation was still wonderful!")
        
        # Show completion status if summary already generated
        elif st.session_state.auto_summary_generated:
            st.info("✅ Our conversation is all saved! Feel free to ask more questions or start fresh anytime. Thanks for being so wonderful to chat with!")

def voice_text_interface(question: str, current_q: int):
    """Combined voice and text interface for interview questions."""
    
    # Get current answer if exists
    current_answer = ""
    if f"question_{current_q + 1}" in st.session_state.candidate_data:
        current_answer = st.session_state.candidate_data[f"question_{current_q + 1}"]["answer"]
    
    # Voice recording section
    if load_voice_modules():
        if st.button("🎤 Let me hear your voice!", key=f"record_{current_q}", disabled=st.session_state.is_listening, help="Click and speak - I'm all ears!"):
            with st.spinner("🎤 Listening..."):
                voice_answer = listen_for_speech()
                st.session_state.is_listening = False
                
                if voice_answer:
                    st.session_state[f"temp_answer_{current_q}"] = voice_answer
                    st.rerun()
                else:
                    st.error("I couldn't quite catch that - no worries! Want to try speaking again or just type your answer?")
    
    # Answer input
    default_text = st.session_state.get(f"temp_answer_{current_q}", current_answer)
    
    answer = st.text_area(
        "Share your thoughts:",
        value=default_text,
        height=120,
        key=f"answer_edit_{current_q}",
        placeholder="I'd love to hear what you have to say - speak or type whatever feels comfortable!"
    )
    
    # Submit button
    button_text = "🎉 That's a wrap!" if current_q == len(get_interview_questions()) - 1 else "✨ Let's continue!"
    
    if st.button(button_text, key=f"submit_{current_q}", disabled=not answer.strip(), help="I'm excited to hear what you have to say!"):
        st.session_state.candidate_data[f"question_{current_q + 1}"] = {
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        }
        if f"temp_answer_{current_q}" in st.session_state:
            del st.session_state[f"temp_answer_{current_q}"]
        
        st.session_state.current_question += 1
        st.rerun()


def display_summary(summary_data: dict):
    """Display interview summary."""
    st.markdown("---")
    st.markdown("## 📊 Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Candidate:** {summary_data.get('name', 'N/A')}")
        st.markdown(f"**Score:** {summary_data.get('overall_score', 'N/A')}/10")
    
    with col2:
        st.markdown(f"**Recommendation:** {summary_data.get('recommendation', 'N/A')}")
    
    if 'strengths' in summary_data and summary_data['strengths']:
        st.markdown("**Strengths:**")
        for strength in summary_data['strengths'][:3]:  # Show top 3
            st.markdown(f"• {strength}")
    
    if 'next_steps' in summary_data:
        st.markdown(f"**Next Steps:** {summary_data['next_steps']}")

def generate_transcript(candidate_data: Dict[str, Any], session_id: str) -> str:
    """Generate transcript from candidate data."""
    lines = [
        "STREAMLIT AI INTERVIEW TRANSCRIPT",
        "=" * 50,
        f"Session ID: {session_id}",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]
    
    for key, data in sorted(candidate_data.items()):
        question_num = key.split('_')[1]
        lines.extend([
            f"Question {question_num}:",
            f"Q: {data['question']}",
            f"A: {data['answer']}",
            f"Timestamp: {data['timestamp']}",
            ""
        ])
    
    lines.extend([
        "=" * 50,
        "END OF INTERVIEW"
    ])
    
    return "\n".join(lines)

def scheduling_page():
    """Scheduling interface."""
    st.title("📅 Interview Scheduling")
    
    try:
        scheduler = get_scheduler()
        
        # Show available slots
        st.markdown("### Available Time Slots")
        available_slots = scheduler.get_available_slots()
        
        if available_slots:
            # Display available slots
            slot_options = {}
            for slot in available_slots[:10]:  # Show first 10 slots
                formatted_time = slot['formatted_time']
                slot_options[formatted_time] = slot['slot_id']
            
            selected_slot_display = st.selectbox("Select Time Slot", list(slot_options.keys()))
            selected_slot_id = slot_options[selected_slot_display]
            
            # Candidate details
            st.markdown("### Candidate Information")
            candidate_name = st.text_input("Candidate Name")
            candidate_email = st.text_input("Email Address")
            candidate_phone = st.text_input("Phone Number (optional)")
            notes = st.text_area("Notes (optional)", height=100)
            
            if st.button("Book Interview"):
                if candidate_name and candidate_email:
                    session_id = scheduler.book_session(
                        candidate_name=candidate_name,
                        candidate_email=candidate_email,
                        candidate_phone=candidate_phone,
                        slot_id=selected_slot_id,
                        notes=notes
                    )
                    if session_id:
                        st.success(f"✅ Interview booked successfully!")
                        st.info(f"Session ID: {session_id}")
                        st.info(f"Time: {selected_slot_display}")
                        st.rerun()
                    else:
                        st.error("Failed to book interview. Please try again.")
                else:
                    st.error("Please fill in Name and Email fields")
        else:
            st.warning("No available time slots found")
        
        # Show scheduled sessions
        st.markdown("---")
        st.markdown("### Scheduled Interviews")
        
        scheduled_sessions = scheduler.get_scheduled_sessions('confirmed')
        if scheduled_sessions:
            for session in scheduled_sessions:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.info(f"**{session['candidate_name']}** - {session['formatted_time']}")
                with col2:
                    if st.button("Cancel", key=f"cancel_{session['session_id']}"):
                        if scheduler.cancel_session(session['session_id']):
                            st.success("Interview cancelled")
                            st.rerun()
        else:
            st.info("No scheduled interviews")
            
    except Exception as e:
        st.error(f"Scheduling system error: {e}")

def sessions_page():
    """View interview sessions."""
    st.title("📊 Interview Sessions")
    
    try:
        logger = InterviewLogger()
        scheduler = get_scheduler()
        
        # Tabs for different views
        tab1, tab2 = st.tabs(["Completed Interviews", "Scheduled Interviews"])
        
        with tab1:
            # Get completed interview sessions
            sessions = logger.get_all_sessions()
            
            if sessions:
                st.markdown(f"### Total Completed Sessions: {len(sessions)}")
                
                for session in sessions:
                    with st.expander(f"Session {session['session_id'][:8]}... - {session['timestamp'][:10]}"):
                        st.markdown(f"**Session ID:** {session['session_id']}")
                        st.markdown(f"**Date:** {session['timestamp']}")
                        
                        if session.get('summary'):
                            try:
                                summary_data = json.loads(session['summary'])
                                st.markdown(f"**Candidate:** {summary_data.get('name', 'N/A')}")
                                st.markdown(f"**Score:** {summary_data.get('overall_score', 'N/A')}/10")
                                st.markdown(f"**Recommendation:** {summary_data.get('recommendation', 'N/A')}")
                            except:
                                st.markdown("**Summary:** Available")
                        
                        if st.button(f"View Transcript", key=f"transcript_{session['session_id']}"):
                            st.text_area("Transcript", session.get('transcript', 'No transcript available'), height=200)
            else:
                st.info("No completed interview sessions found")
        
        with tab2:
            # Get scheduled sessions
            scheduled = scheduler.get_scheduled_sessions()
            
            if scheduled:
                st.markdown(f"### Total Scheduled Sessions: {len(scheduled)}")
                
                for session in scheduled:
                    status_color = {
                        'confirmed': '🟢',
                        'cancelled': '🔴', 
                        'completed': '✅'
                    }.get(session['status'], '⚪')
                    
                    with st.expander(f"{status_color} {session['candidate_name']} - {session['formatted_time']}"):
                        st.markdown(f"**Session ID:** {session['session_id']}")
                        st.markdown(f"**Candidate:** {session['candidate_name']}")
                        st.markdown(f"**Email:** {session['candidate_email']}")
                        st.markdown(f"**Time:** {session['formatted_time']}")
                        st.markdown(f"**Status:** {session['status']}")
                        if session['notes']:
                            st.markdown(f"**Notes:** {session['notes']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if session['status'] == 'confirmed' and st.button("Cancel", key=f"cancel_session_{session['session_id']}"):
                                if scheduler.cancel_session(session['session_id']):
                                    st.success("Session cancelled")
                                    st.rerun()
                        with col2:
                            if session['status'] == 'confirmed' and st.button("Mark Complete", key=f"complete_{session['session_id']}"):
                                if scheduler.complete_session(session['session_id']):
                                    st.success("Session marked as completed")
                                    st.rerun()
            else:
                st.info("No scheduled sessions found")
            
    except Exception as e:
        st.error(f"Error loading sessions: {e}")

def main():
    """Main Streamlit application."""
    initialize_session_state()
    sidebar_navigation()
    
    # Route to appropriate page
    if st.session_state.current_page == "Home":
        home_page()
    elif st.session_state.current_page == "Interview":
        interview_page()
    elif st.session_state.current_page == "Scheduling":
        scheduling_page()
    elif st.session_state.current_page == "Sessions":
        sessions_page()

if __name__ == "__main__":
    main()
