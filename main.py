import os
from datetime import datetime
from interview_flow import conduct_interview
from summarizer import summarize_candidate
from logger import InterviewLogger, generate_session_id

def main():
    """
    Main function to run the AI interview agent with logging and session memory.
    """
    print("🎯 Starting AI Interview Agent with Logging & Session Memory...")
    print("=" * 60)
    
    # Initialize the logger
    logger = InterviewLogger()
    
    # Check for required environment variables
    if not os.getenv('GOOGLE_API_KEY'):
        print("⚠️  Warning: GOOGLE_API_KEY not found in environment variables.")
        print("   Please create a .env file with your Google API key.")
        print("   The interview will continue without Gemini Pro integration.")
    
    # Conduct the interview
    print("\n📝 Starting interview session...")
    candidate_data = conduct_interview()
    
    # Generate transcript from interview data
    transcript = generate_transcript(candidate_data)
    
    # Generate AI summary using the summarizer
    print("\n🤖 Generating interview summary...")
    try:
        summary = summarize_candidate(candidate_data)
        print("✓ Summary generated successfully!")
    except Exception as e:
        print(f"⚠️  Warning: Could not generate AI summary: {e}")
        summary = "Summary generation failed. Manual review required."
    
    # Generate unique session ID and save to database
    session_id = generate_session_id()
    print(f"\n💾 Saving interview session: {session_id}")
    
    success = logger.save_session(session_id, transcript, summary)
    
    if success:
        print("✅ Interview session saved successfully!")
        
        # Display session summary
        print("\n" + "=" * 60)
        print("📊 INTERVIEW SESSION SUMMARY")
        print("=" * 60)
        print(f"Session ID: {session_id}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Questions: {len(candidate_data)}")
        
        # Show summary
        print(f"\n📋 AI Summary:")
        print("-" * 40)
        print(summary)
        
        # Show database stats
        total_sessions = logger.get_session_count()
        print(f"\n📈 Database Statistics:")
        print(f"   Total sessions stored: {total_sessions}")
        
    else:
        print("❌ Failed to save interview session!")
    
    print("\n" + "=" * 60)
    print("🎉 Interview session completed!")
    print("=" * 60)
    
    return {
        'session_id': session_id,
        'candidate_data': candidate_data,
        'transcript': transcript,
        'summary': summary,
        'saved_successfully': success
    }

def generate_transcript(candidate_data: dict) -> str:
    """
    Generate a transcript from the interview data.
    
    Args:
        candidate_data (dict): Dictionary containing interview questions and answers
        
    Returns:
        str: Formatted transcript of the interview
    """
    transcript_lines = []
    transcript_lines.append("AI INTERVIEW TRANSCRIPT")
    transcript_lines.append("=" * 50)
    transcript_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    transcript_lines.append("")
    
    for key, data in candidate_data.items():
        question_num = key.split('_')[1]
        transcript_lines.append(f"Question {question_num}:")
        transcript_lines.append(f"Q: {data['question']}")
        transcript_lines.append(f"A: {data['answer']}")
        transcript_lines.append("")
    
    transcript_lines.append("=" * 50)
    transcript_lines.append("END OF INTERVIEW")
    
    return "\n".join(transcript_lines)

if __name__ == "__main__":
    try:
        result = main()
        print(f"\n🔍 Session ID for future reference: {result['session_id']}")
    except KeyboardInterrupt:
        print("\n\n⚠️  Interview interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your configuration and try again.")
