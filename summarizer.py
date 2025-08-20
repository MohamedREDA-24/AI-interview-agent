import json
from typing import Dict, Any

class InterviewSummarizer:
    """
    Simple interview summarization module that extracts key information
    from candidate responses without complex AI dependencies.
    """
    
    def __init__(self):
        """Initialize the summarizer."""
        pass
    
    def summarize_candidate(self, candidate_data: Dict[str, Any]) -> str:
        """
        Summarize candidate interview responses into structured JSON.
        
        Args:
            candidate_data (dict): Dictionary containing candidate responses
                Format: {
                    "question_1": {"question": "...", "answer": "..."},
                    "question_2": {"question": "...", "answer": "..."},
                    ...
                }
        
        Returns:
            str: JSON string summary with structured fields
        """
        try:
            # Extract key information from responses
            summary = self._extract_summary_data(candidate_data)
            
            # Convert to JSON
            return json.dumps(summary, indent=2)
            
        except Exception as e:
            print(f"Summarization failed: {e}")
            return self._fallback_summary(candidate_data)
    
    def _extract_summary_data(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure summary data from candidate responses."""
        
        # Initialize summary structure
        summary = {
            "name": "Not specified",
            "background": "Not specified", 
            "interest": "Not specified",
            "experience": "Not specified",
            "goals": "Not specified",
            "readiness": "Not specified",
            "assessment": "Interview completed",
            "strengths": [],
            "concerns": [],
            "recommendation": "Moderate"
        }
        
        # Extract name from first question (usually background)
        if "question_1" in candidate_data:
            answer = candidate_data["question_1"].get("answer", "")
            if answer and len(answer) > 10:
                # Look for "My name is" pattern and extract the actual name
                if "my name is" in answer.lower():
                    name_start = answer.lower().find("my name is") + len("my name is")
                    name_part = answer[name_start:].strip()
                    # Take first few words after "my name is"
                    name_words = name_part.split()[:2]  # Usually first and last name
                    if name_words:
                        # Clean up the name (remove periods, commas, etc.)
                        clean_name = " ".join(name_words).rstrip('.,!?')
                        summary["name"] = clean_name
                else:
                    # Fallback: take first few words
                    words = answer.split()[:2]
                    clean_name = " ".join(words).rstrip('.,!?')
                    summary["name"] = clean_name
        
        # Extract background from first question
        if "question_1" in candidate_data:
            answer = candidate_data["question_1"].get("answer", "")
            if answer:
                # Extract key background info
                background_keywords = ["degree", "university", "college", "experience", "years", "worked"]
                background_parts = []
                sentences = answer.split('.')
                for sentence in sentences:
                    if any(keyword in sentence.lower() for keyword in background_keywords):
                        background_parts.append(sentence.strip())
                if background_parts:
                    summary["background"] = ". ".join(background_parts[:2])
        
        # Extract interest from second question
        if "question_2" in candidate_data:
            answer = candidate_data["question_2"].get("answer", "")
            if answer:
                # Extract motivation
                interest_keywords = ["passionate", "interested", "want", "goal", "opportunity"]
                for keyword in interest_keywords:
                    if keyword in answer.lower():
                        start_idx = answer.lower().find(keyword)
                        # Find the end of the sentence or take more context
                        sentence_end = answer.find('.', start_idx)
                        if sentence_end != -1:
                            end_idx = sentence_end + 1
                        else:
                            end_idx = min(start_idx + 120, len(answer))
                        summary["interest"] = answer[start_idx:end_idx].strip().rstrip('.,!?')
                        break
        
        # Extract experience from third question
        if "question_3" in candidate_data:
            answer = candidate_data["question_3"].get("answer", "")
            if answer:
                # Extract technical skills
                tech_keywords = ["python", "machine learning", "ai", "data science", "tensorflow", "scikit-learn", "deep learning"]
                tech_skills = []
                for keyword in tech_keywords:
                    if keyword in answer.lower():
                        tech_skills.append(keyword)
                if tech_skills:
                    summary["experience"] = f"Experience with: {', '.join(tech_skills)}"
        
        # Extract goals from fourth question
        if "question_4" in candidate_data:
            answer = candidate_data["question_4"].get("answer", "")
            if answer:
                # Extract goal information
                goal_keywords = ["short-term", "long-term", "goal", "aim", "become"]
                for keyword in goal_keywords:
                    if keyword in answer.lower():
                        start_idx = answer.lower().find(keyword)
                        # Find the end of the sentence or take more context
                        sentence_end = answer.find('.', start_idx)
                        if sentence_end != -1:
                            end_idx = sentence_end + 1
                        else:
                            end_idx = min(start_idx + 100, len(answer))
                        summary["goals"] = answer[start_idx:end_idx].strip().rstrip('.,!?')
                        break
        
        # Extract readiness from fifth question
        if "question_5" in candidate_data:
            answer = candidate_data["question_5"].get("answer", "")
            if answer:
                if "immediately" in answer.lower() or "now" in answer.lower():
                    summary["readiness"] = "Available immediately"
                elif "month" in answer.lower() or "week" in answer.lower():
                    summary["readiness"] = "Available within a month"
                else:
                    summary["readiness"] = "Timeline not specified"
        
        # Generate assessment and recommendation
        summary = self._generate_assessment(summary)
        
        return summary
    
    def _generate_assessment(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate assessment and recommendation based on extracted data."""
        
        # Analyze strengths
        strengths = []
        if summary["background"] != "Not specified":
            strengths.append("Strong educational background")
        if summary["experience"] != "Not specified":
            strengths.append("Technical skills demonstrated")
        if "immediately" in summary["readiness"].lower():
            strengths.append("Available immediately")
        if summary["goals"] != "Not specified":
            strengths.append("Clear career objectives")
        
        summary["strengths"] = strengths if strengths else ["Interview completed successfully"]
        
        # Analyze concerns
        concerns = []
        if summary["background"] == "Not specified":
            concerns.append("Background information unclear")
        if summary["experience"] == "Not specified":
            concerns.append("Technical experience not detailed")
        if "not specified" in summary["readiness"].lower():
            concerns.append("Availability timeline unclear")
        
        summary["concerns"] = concerns
        
        # Generate recommendation
        strength_score = len(summary["strengths"])
        concern_score = len(summary["concerns"])
        
        if strength_score >= 3 and concern_score <= 1:
            summary["recommendation"] = "Strong"
        elif strength_score >= 2 and concern_score <= 2:
            summary["recommendation"] = "Moderate"
        else:
            summary["recommendation"] = "Weak"
        
        # Generate overall assessment
        if summary["recommendation"] == "Strong":
            summary["assessment"] = "Strong candidate with clear qualifications and goals"
        elif summary["recommendation"] == "Moderate":
            summary["assessment"] = "Moderate candidate with some areas for improvement"
        else:
            summary["assessment"] = "Candidate needs significant development in key areas"
        
        return summary
    
    def _fallback_summary(self, candidate_data: Dict[str, Any]) -> str:
        """Generate a basic fallback summary."""
        fallback = {
            "name": "Extraction failed",
            "background": "Information not available",
            "interest": "Not specified",
            "experience": "Not specified",
            "goals": "Not specified",
            "readiness": "Not specified",
            "assessment": "Summary generation failed",
            "strengths": ["Interview completed"],
            "concerns": ["Data extraction issues"],
            "recommendation": "Review required"
        }
        return json.dumps(fallback, indent=2)
    
    def validate_summary(self, summary_json: str) -> bool:
        """
        Validate that the summary JSON contains all required fields.
        
        Args:
            summary_json (str): JSON string to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            data = json.loads(summary_json)
            required_fields = [
                "name", "background", "interest", "experience", 
                "goals", "readiness", "assessment", 
                "strengths", "concerns", "recommendation"
            ]
            
            for field in required_fields:
                if field not in data:
                    print(f"Missing required field: {field}")
                    return False
            
            return True
            
        except json.JSONDecodeError:
            print("Invalid JSON format")
            return False
        except Exception as e:
            print(f"Validation error: {e}")
            return False


def create_summarizer() -> InterviewSummarizer:
    """
    Factory function to create a summarizer instance.
    
    Returns:
        InterviewSummarizer: Configured summarizer instance
    """
    return InterviewSummarizer()


def summarize_candidate(candidate_data: Dict[str, Any]) -> str:
    """
    Convenience function to summarize candidate responses.
    
    Args:
        candidate_data (dict): Dictionary containing candidate responses
        
    Returns:
        str: JSON string summary
    """
    summarizer = create_summarizer()
    return summarizer.summarize_candidate(candidate_data)


if __name__ == "__main__":
    """
    Test block for the summarization module.
    """
    print("=" * 70)
    print("INTERVIEW SUMMARIZATION MODULE TEST")
    print("=" * 70)
    
    # Sample candidate data for testing
    sample_candidate_data = {
        "question_1": {
            "question": "What is your full name and background?",
            "answer": "My name is Sarah Johnson. I have a Bachelor's degree in Computer Science from MIT and 3 years of experience as a software engineer at Google. I've worked on machine learning projects and have a strong foundation in Python and data analysis."
        },
        "question_2": {
            "question": "Why are you interested in joining the program?",
            "answer": "I'm passionate about AI and want to transition from software engineering to data science. This program seems like the perfect opportunity to gain hands-on experience with real-world AI projects and learn from industry experts."
        },
        "question_3": {
            "question": "What's your experience with data science or AI?",
            "answer": "I've taken several online courses in machine learning and have implemented basic ML models in my projects. I'm comfortable with scikit-learn, TensorFlow, and have some experience with deep learning. I've also worked with large datasets and understand data preprocessing."
        },
        "question_4": {
            "question": "What are your short-term and long-term goals?",
            "answer": "Short-term, I want to become proficient in advanced ML algorithms and gain experience with real-world datasets. Long-term, I aim to become a senior data scientist and eventually lead AI initiatives in healthcare technology."
        },
        "question_5": {
            "question": "Are you ready to start immediately? If not, when?",
            "answer": "Yes, I can start immediately. I've already given my notice at Google and will be available full-time starting next month. I'm excited to begin this new chapter in my career."
        }
    }
    
    print("Sample candidate data created for testing...")
    
    # Test summarization
    print("\n1. Testing interview summarization...")
    summarizer = create_summarizer()
    
    # Generate summary
    summary = summarizer.summarize_candidate(sample_candidate_data)
    
    print("\n2. Generated Summary:")
    print("-" * 50)
    print(summary)
    print("-" * 50)
    
    # Validate summary
    print("\n3. Validating summary format...")
    if summarizer.validate_summary(summary):
        print("✓ Summary validation passed")
    else:
        print("✗ Summary validation failed")
    
    # Test JSON parsing
    try:
        parsed_summary = json.loads(summary)
        print(f"✓ JSON parsing successful")
        print(f"✓ Extracted {len(parsed_summary)} fields")
        
        # Show key information
        if "name" in parsed_summary:
            print(f"✓ Candidate name: {parsed_summary['name']}")
        if "recommendation" in parsed_summary:
            print(f"✓ Recommendation: {parsed_summary['recommendation']}")
            
    except json.JSONDecodeError as e:
        print(f"✗ JSON parsing failed: {e}")
    
    print("\n" + "=" * 70)
    print("Test completed! Interview summarization module is ready for integration.")
    print("=" * 70)
