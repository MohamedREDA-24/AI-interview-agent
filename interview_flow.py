import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def ask_gemini(prompt: str) -> str:
    """
    Send a prompt to Gemini Pro and return the response text.
    
    Args:
        prompt (str): The prompt to send to Gemini Pro
        
    Returns:
        str: The response text from Gemini Pro
    """
    try:
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        model = genai.GenerativeModel('gemini-pro')
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error communicating with Gemini Pro: {e}")
        return "I'm having trouble processing your request right now."

def is_answer_clear(answer: str) -> bool:
    """
    Check if an answer is clear enough (not too short or empty).
    
    Args:
        answer (str): The candidate's answer
        
    Returns:
        bool: True if answer is clear, False otherwise
    """
    if not answer or len(answer.strip()) < 10:
        return False
    return True

def clarify_question(question: str, previous_answer: str) -> str:
    """
    Create a clarification prompt when an answer is unclear.
    
    Args:
        question (str): The original question
        previous_answer (str): The previous unclear answer
        
    Returns:
        str: A clarification prompt
    """
    return f"Your previous answer was quite brief: '{previous_answer}'. Could you please provide more detail for: {question}"

def conduct_interview() -> dict:
    """
    Conduct the interview by asking questions and collecting responses.
    
    Returns:
        dict: Dictionary containing all candidate responses
    """
    questions = [
        "What is your full name and background?",
        "Why are you interested in joining the program?",
        "What's your experience with data science or AI?",
        "What are your short-term and long-term goals?",
        "Are you ready to start immediately? If not, when?"
    ]
    
    candidate_data = {}
    
    print("Welcome to the AI Interview Agent!")
    print("=" * 50)
    
    for i, question in enumerate(questions, 1):
        print(f"\nQuestion {i}: {question}")
        
        answer = input("Your answer: ").strip()
        
        while not is_answer_clear(answer):
            print("\nYour answer was quite brief. Let me ask for clarification:")
            clarification = clarify_question(question, answer)
            print(f"Clarification: {clarification}")
            answer = input("Your detailed answer: ").strip()
        
        question_key = f"question_{i}"
        candidate_data[question_key] = {
            "question": question,
            "answer": answer
        }
        
        print(f"✓ Answer recorded for question {i}")
    
    return candidate_data

def main():
    """
    Main function to run the interview flow.
    """
    print("Starting AI Interview Agent with Gemini Pro...")
    
    if not os.getenv('GOOGLE_API_KEY'):
        print("Warning: GOOGLE_API_KEY not found in environment variables.")
        print("Please create a .env file with your Google API key.")
        print("The interview will continue without Gemini Pro integration.")
    
    candidate_data = conduct_interview()
    
    print("\n" + "=" * 50)
    print("INTERVIEW COMPLETED - COLLECTED DATA:")
    print("=" * 50)
    
    for key, data in candidate_data.items():
        print(f"\n{key.upper()}:")
        print(f"Question: {data['question']}")
        print(f"Answer: {data['answer']}")
    
    print("\n" + "=" * 50)
    print("Interview session completed successfully!")
    
    return candidate_data

if __name__ == "__main__":
    main() 