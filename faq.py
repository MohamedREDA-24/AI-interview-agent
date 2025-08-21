import json
import os
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class FAQModule:
    """
    FAQ Q&A module using TF-IDF vectorization and cosine similarity
    to find the most relevant answers to user questions.
    """
    
    def __init__(self, faq_file: str = "faq.json"):
        """
        Initialize the FAQ module.
        
        Args:
            faq_file (str): Path to FAQ JSON file, or use default hardcoded data
        """
        self.faq_data = self._load_faq_data(faq_file)
        self.questions = list(self.faq_data.keys())
        self.answers = list(self.faq_data.values())
        self.vectorizer = None
        self.question_vectors = None
        self._initialize_vectorizer()
    
    def _load_faq_data(self, faq_file: str) -> Dict[str, str]:
        """
        Load FAQ data from JSON file or use default hardcoded data.
        
        Args:
            faq_file (str): Path to FAQ JSON file
            
        Returns:
            Dict[str, str]: FAQ question-answer pairs
        """
        # Try to load from JSON file first
        if os.path.exists(faq_file):
            try:
                with open(faq_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Warning: Could not load {faq_file}: {e}")
                print("   Using default hardcoded FAQ data.")
        
        # Default hardcoded FAQ data
        return {
            "what is the cost of the program?": "The program costs $500 for the complete course package, which includes all materials, access to our learning platform, and certification upon completion.",
            "do I need a technical background?": "No, beginners are welcome! While some basic computer skills are helpful, we start from the fundamentals and build up. Our program is designed to accommodate various skill levels.",
            "can I do this part-time?": "Yes, absolutely! The program is designed to be flexible and can be completed part-time. Most students spend 10-15 hours per week and complete the program in 3-6 months.",
            "how long does the program take?": "The program typically takes 3-6 months to complete, depending on your pace and time commitment. Full-time students can finish in 3 months, while part-time students usually take 4-6 months.",
            "what will I learn in this program?": "You'll learn fundamental AI concepts, machine learning algorithms, data preprocessing, model training, and real-world project implementation. The curriculum covers Python programming, statistics, and practical AI applications.",
            "is there a certificate upon completion?": "Yes! Upon successful completion of the program, you'll receive a professional certificate that's recognized by industry partners and can be added to your resume and LinkedIn profile.",
            "do you provide job placement assistance?": "Yes, we offer career support including resume building, interview preparation, and connections to our industry partner network. Many of our graduates find positions within 3 months of completion.",
            "what are the prerequisites?": "Basic computer literacy, high school mathematics, and a willingness to learn are the main prerequisites. No prior programming experience is required, though it can be helpful.",
            "can I access the materials after completion?": "Yes, you'll have lifetime access to all course materials, updates, and the learning platform. This allows you to review concepts and stay current with new developments.",
            "is there a money-back guarantee?": "We offer a 30-day money-back guarantee. If you're not satisfied with the program within the first 30 days, we'll provide a full refund, no questions asked.",
            "what support is available during the program?": "You'll have access to our community forum, weekly office hours with instructors, and direct support through our help desk. We're committed to your success throughout the program.",
            "are there any additional costs?": "The $500 covers everything you need to complete the program. There are no hidden fees or additional costs for software, tools, or materials.",
            "can I start anytime?": "Yes! Our program is self-paced and you can start whenever you're ready. New cohorts begin monthly, but you can begin your learning journey at any time.",
            "what if I fall behind or need more time?": "No problem! The program is designed to be flexible. You can take breaks when needed and resume where you left off. We want you to succeed at your own pace.",
            "do you offer payment plans?": "Yes, we offer flexible payment plans. You can pay the full $500 upfront or choose from our installment options: 2 payments of $275 or 3 payments of $190."
        }
    
    def _initialize_vectorizer(self):
        """Initialize the TF-IDF vectorizer and compute question vectors."""
        try:
            self.vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words='english',
                ngram_range=(1, 3),
                max_features=2000,
                min_df=1,
                max_df=1.0
            )
            
            # Fit and transform the questions
            self.question_vectors = self.vectorizer.fit_transform(self.questions)
            print(f"✓ FAQ module initialized with {len(self.questions)} questions")
            
        except Exception as e:
            print(f"❌ Error initializing FAQ vectorizer: {e}")
            self.vectorizer = None
            self.question_vectors = None
    
    def get_faq_answer(self, query: str, similarity_threshold: float = 0.4) -> str:
        """
        Find the most relevant FAQ answer for a given query.
        
        Args:
            query (str): User's question
            similarity_threshold (float): Minimum similarity score to consider a match
            
        Returns:
            str: Best matching answer or fallback response
        """
        if not self.vectorizer or self.question_vectors is None:
            return "I'm sorry, the FAQ system is not available right now."
        
        try:
            # First try keyword matching for better accuracy
            query_lower = query.lower()
            keyword_matches = []
            
            for i, question in enumerate(self.questions):
                question_lower = question.lower()
                
                # Check for exact phrase matches first (highest priority)
                if any(phrase in query_lower for phrase in ["cost", "price", "fee", "how much"]) and any(phrase in question_lower for phrase in ["cost", "price", "fee"]):
                    score = 15  # Highest score for cost-related questions
                elif any(phrase in query_lower for phrase in ["certificate", "certification"]) and any(phrase in question_lower for phrase in ["certificate", "certification"]):
                    score = 10  # High score for certificate-related questions
                elif any(phrase in query_lower for phrase in ["background", "prerequisites", "requirements", "need to know", "do i need"]) and any(phrase in question_lower for phrase in ["background", "prerequisites", "requirements", "technical background"]):
                    score = 12   # High score for requirement-related questions
                elif any(phrase in query_lower for phrase in ["part-time", "flexible", "work while"]) and any(phrase in question_lower for phrase in ["part-time", "flexible"]):
                    score = 8   # High score for flexibility-related questions
                elif any(phrase in query_lower for phrase in ["guarantee", "refund", "satisfied"]) and any(phrase in question_lower for phrase in ["guarantee", "refund"]):
                    score = 8   # High score for guarantee-related questions
                else:
                    # General keyword matching
                    key_terms = ["program", "duration", "time", "technical", "support", "materials"]
                    score = 0
                    for term in key_terms:
                        if term in query_lower and term in question_lower:
                            score += 1
                
                if score > 0:
                    keyword_matches.append((i, score))
            
            # Use keyword matching if we found good matches
            if keyword_matches:
                # Sort by score and use the best match
                keyword_matches.sort(key=lambda x: x[1], reverse=True)
                best_keyword_idx = keyword_matches[0][0]
                best_question = self.questions[best_keyword_idx]
                best_answer = self.answers[best_keyword_idx]
                
                print(f"🔍 FAQ Match (Keyword): '{query}' → '{best_question}' (keyword score: {keyword_matches[0][1]})")
                return best_answer
            
            # Fallback to TF-IDF similarity if no keyword matches
            query_vector = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vector, self.question_vectors).flatten()
            best_match_idx = np.argmax(similarities)
            best_similarity = similarities[best_match_idx]
            
            # If TF-IDF similarity is good, use it
            if best_similarity >= similarity_threshold:
                best_question = self.questions[best_match_idx]
                best_answer = self.answers[best_match_idx]
                
                print(f"🔍 FAQ Match (TF-IDF): '{query}' → '{best_question}' (similarity: {best_similarity:.3f})")
                return best_answer
            
            print(f"❓ No FAQ match found for: '{query}' (TF-IDF similarity: {best_similarity:.3f})")
            return "I don't have a specific answer for that question. Could you please rephrase it or ask something else?"
                
        except Exception as e:
            print(f"❌ Error in FAQ matching: {e}")
            return "I'm sorry, I encountered an error while searching the FAQ. Please try again."
    
    def get_similar_questions(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Get top-k most similar questions for a given query.
        
        Args:
            query (str): User's question
            top_k (int): Number of similar questions to return
            
        Returns:
            List[Tuple[str, float]]: List of (question, similarity_score) tuples
        """
        if not self.vectorizer or self.question_vectors is None:
            return []
        
        try:
            query_vector = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vector, self.question_vectors).flatten()
            
            # Get top-k indices
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:
                    results.append((self.questions[idx], similarities[idx]))
            
            return results
            
        except Exception as e:
            print(f"❌ Error getting similar questions: {e}")
            return []
    
    def add_faq_item(self, question: str, answer: str) -> bool:
        """
        Add a new FAQ item to the dataset.
        
        Args:
            question (str): New question
            answer (str): Corresponding answer
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.faq_data[question] = answer
            self.questions.append(question)
            self.answers.append(answer)
            
            # Reinitialize vectorizer with new data
            self._initialize_vectorizer()
            
            print(f"✓ Added new FAQ item: '{question}'")
            return True
            
        except Exception as e:
            print(f"❌ Error adding FAQ item: {e}")
            return False
    
    def save_faq_data(self, filename: str = "faq.json") -> bool:
        """
        Save FAQ data to a JSON file.
        
        Args:
            filename (str): Output filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.faq_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ FAQ data saved to {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving FAQ data: {e}")
            return False
    
    def get_faq_stats(self) -> Dict[str, int]:
        """
        Get statistics about the FAQ dataset.
        
        Returns:
            Dict[str, int]: Statistics including total questions, average answer length, etc.
        """
        total_questions = len(self.questions)
        avg_answer_length = np.mean([len(answer) for answer in self.answers]) if self.answers else 0
        
        return {
            "total_questions": total_questions,
            "average_answer_length": round(avg_answer_length, 1),
            "shortest_answer": min([len(answer) for answer in self.answers]) if self.answers else 0,
            "longest_answer": max([len(answer) for answer in self.answers]) if self.answers else 0
        }

def is_question_like(text: str) -> bool:
    """
    Check if text looks like a question.
    
    Args:
        text (str): Text to check
        
    Returns:
        bool: True if text appears to be a question
    """
    question_starters = [
        "what", "how", "do", "can", "could", "would", "will", "should", "is", "are", "does",
        "when", "where", "why", "which", "who", "whose", "whom", "if", "whether"
    ]
    
    text_lower = text.lower().strip()
    
    # Check if starts with question word
    for starter in question_starters:
        if text_lower.startswith(starter):
            return True
    
    # Check if ends with question mark
    if text_lower.endswith("?"):
        return True
    
    # Check if contains question indicators
    question_indicators = ["tell me", "explain", "describe", "help me", "i want to know", "cost", "price", "fee"]
    for indicator in question_indicators:
        if indicator in text_lower:
            return True
    
    # Check for specific keywords that indicate questions
    question_keywords = ["cost", "price", "fee", "duration", "time", "prerequisites", "requirements", "certificate", "guarantee", "refund"]
    for keyword in question_keywords:
        if keyword in text_lower:
            return True
    
    return False

# Test block
if __name__ == "__main__":
    print("🧪 Testing FAQ Module...")
    print("=" * 50)
    
    # Initialize FAQ module
    faq = FAQModule()
    
    # Test queries
    test_queries = [
        "How much does the program cost?",
        "Do I need to know programming?",
        "Can I work while studying?",
        "What if I'm not satisfied?",
        "Tell me about the certificate",
        "Random unrelated text here"
    ]
    
    print("\n📝 Testing FAQ matching:")
    print("-" * 40)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        answer = faq.get_faq_answer(query)
        print(f"Answer: {answer}")
    
    # Test similar questions
    print(f"\n🔍 Testing similar questions for 'cost':")
    similar = faq.get_similar_questions("cost", top_k=3)
    for question, similarity in similar:
        print(f"  - {question} (similarity: {similarity:.3f})")
    
    # Show statistics
    print(f"\n📊 FAQ Statistics:")
    stats = faq.get_faq_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ FAQ module test completed!")
