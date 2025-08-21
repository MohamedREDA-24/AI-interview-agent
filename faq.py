import json
import os
from typing import Dict, List, Tuple
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("⚠️  sentence-transformers not available. Install with: pip install sentence-transformers")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

class FAQModule:
    """
    FAQ Q&A module using Sentence Transformers for semantic similarity
    to find the most relevant answers to user questions.
    """
    
    def __init__(self, faq_file: str = "faq.json", model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the FAQ module.
        
        Args:
            faq_file (str): Path to FAQ JSON file, or use default hardcoded data
            model_name (str): Sentence transformer model to use
        """
        self.faq_data = self._load_faq_data(faq_file)
        self.questions = list(self.faq_data.keys())
        self.answers = list(self.faq_data.values())
        self.model = None
        self.question_embeddings = None
        self.model_name = model_name
        self._initialize_model()
    
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
    
    def _initialize_model(self):
        """Initialize the Sentence Transformer model and compute question embeddings."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            print("❌ Sentence Transformers not available. Please install with: pip install sentence-transformers")
            return
            
        try:
            print(f"🔄 Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            
            # Encode all questions to get embeddings
            print("🔄 Computing question embeddings...")
            self.question_embeddings = self.model.encode(self.questions)
            print(f"✓ FAQ module initialized with {len(self.questions)} questions using Sentence Transformers")
            
        except Exception as e:
            print(f"❌ Error initializing Sentence Transformer model: {e}")
            self.model = None
            self.question_embeddings = None
    
    def get_faq_answer(self, query: str, similarity_threshold: float = 0.5) -> str:
        """
        Find the most relevant FAQ answer for a given query using semantic similarity.
        
        Args:
            query (str): User's question
            similarity_threshold (float): Minimum similarity score to consider a match
            
        Returns:
            str: Best matching answer or fallback response
        """
        if not self.model or self.question_embeddings is None:
            return "I'm sorry, the FAQ system is not available right now."
        
        try:
            # Encode the user query
            query_embedding = self.model.encode([query])
            
            # Calculate cosine similarity between query and all questions
            similarities = cosine_similarity(query_embedding, self.question_embeddings).flatten()
            
            # Find the best match
            best_match_idx = np.argmax(similarities)
            best_similarity = similarities[best_match_idx]
            
            # Check if similarity meets threshold
            if best_similarity >= similarity_threshold:
                best_question = self.questions[best_match_idx]
                best_answer = self.answers[best_match_idx]
                
                print(f"🔍 FAQ Match (Semantic): '{query}' → '{best_question}' (similarity: {best_similarity:.3f})")
                return best_answer
            else:
                print(f"❓ No FAQ match found for: '{query}' (best similarity: {best_similarity:.3f})")
                return "I don't have a specific answer for that question. Could you please rephrase it or ask something else?"
                
        except Exception as e:
            print(f"❌ Error in FAQ matching: {e}")
            return "I'm sorry, I encountered an error while searching the FAQ. Please try again."
    
    def get_similar_questions(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Get top-k most similar questions for a given query using semantic similarity.
        
        Args:
            query (str): User's question
            top_k (int): Number of similar questions to return
            
        Returns:
            List[Tuple[str, float]]: List of (question, similarity_score) tuples
        """
        if not self.model or self.question_embeddings is None:
            return []
        
        try:
            query_embedding = self.model.encode([query])
            similarities = cosine_similarity(query_embedding, self.question_embeddings).flatten()
            
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
            
            # Reinitialize model with new data
            self._initialize_model()
            
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
    print("🧪 Testing FAQ Module with Sentence Transformers...")
    print("=" * 60)
    
    # Initialize FAQ module
    faq = FAQModule()
    
    # Test queries (including variations and paraphrases)
    test_queries = [
        "How much does the program cost?",
        "What's the price of this course?",
        "Do I need to know programming?",
        "Can I work while studying?",
        "Is it possible to do this part-time?",
        "What if I'm not satisfied?",
        "Tell me about the certificate",
        "Do you provide any certification?",
        "How long will this take?",
        "Random unrelated text here"
    ]
    
    print("\n📝 Testing semantic FAQ matching:")
    print("-" * 50)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        answer = faq.get_faq_answer(query)
        print(f"Answer: {answer[:100]}..." if len(answer) > 100 else f"Answer: {answer}")
    
    # Test similar questions
    print(f"\n🔍 Testing similar questions for 'programming background':")
    similar = faq.get_similar_questions("programming background", top_k=3)
    for question, similarity in similar:
        print(f"  - {question} (similarity: {similarity:.3f})")
    
    # Show statistics
    print(f"\n📊 FAQ Statistics:")
    stats = faq.get_faq_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ FAQ module test completed!")
