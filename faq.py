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
            "what is the cost of the program?": "Great question! Our program is $500 for everything - that's your complete course package with all materials, full access to our learning platform, and your certification when you graduate. We think it's pretty great value for everything you get!",
            "do I need a technical background?": "Not at all! We absolutely love working with beginners. While having some basic computer skills helps, we really do start from the ground up. Our program is specifically designed for people from all different backgrounds - that's what makes our community so amazing!",
            "can I do this part-time?": "Absolutely! We totally get that life is busy. Most of our students are juggling work, family, or other commitments. Typically, folks spend about 10-15 hours per week on the program and finish in 3-6 months. It's completely flexible to fit your schedule.",
            "how long does the program take?": "It really depends on you and your schedule! If you're going full-time, you could wrap up in about 3 months. Most part-time students take around 4-6 months, but honestly, we want you to go at whatever pace works best for you.",
            "what will I learn in this program?": "Oh, you're going to love this! You'll dive into fundamental AI concepts, machine learning algorithms, data preprocessing, and model training. Plus, you'll work on real-world projects that you can actually show off to employers. We cover Python programming, statistics, and tons of practical AI applications.",
            "is there a certificate upon completion?": "Yes! You'll get a professional certificate that our industry partners recognize. It looks great on your resume and LinkedIn profile - our graduates are always excited to show it off!",
            "do you provide job placement assistance?": "We sure do! We're really invested in your success beyond the program. We help with resume building, interview prep, and we'll connect you with our network of industry partners. It's pretty exciting - many of our graduates land positions within 3 months!",
            "what are the prerequisites?": "Keep it simple! You just need basic computer skills, high school level math, and most importantly - enthusiasm to learn! No programming experience required, though if you have some, that's a nice bonus.",
            "can I access the materials after completion?": "Forever and always! Once you're in, you're in for life. You'll have access to all materials, any updates we make, and the full learning platform. It's great for refreshing your knowledge or keeping up with new developments.",
            "is there a money-back guarantee?": "Absolutely! We offer a full 30-day money-back guarantee. If for any reason you're not happy with the program in your first month, just let us know and we'll refund everything, no questions asked. We're that confident you'll love it!",
            "what support is available during the program?": "We've got your back! You'll have access to our amazing community forum, weekly office hours with instructors (they're really helpful!), and direct support through our help desk. We're genuinely committed to seeing you succeed.",
            "are there any additional costs?": "Nope! That $500 covers absolutely everything. No surprise fees, no hidden costs for software or tools. What you see is what you get - we believe in keeping things transparent and simple.",
            "can I start anytime?": "Yes! That's one of the best parts - you can start whenever you're ready. While we have new cohorts starting monthly, you can jump into your learning journey at any time that works for you.",
            "what if I fall behind or need more time?": "Life happens, and we totally get that! The program is super flexible - you can take breaks when you need them and pick up right where you left off. We want you to succeed at your own pace, not ours.",
            "do you offer payment plans?": "We do! We know $500 upfront isn't always easy, so you can choose what works for you: pay it all at once, split it into 2 payments of $275, or spread it over 3 payments of $190. Whatever makes it easier for you!"
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
            return "I'm so sorry, but I'm having some technical difficulties with my knowledge base right now. Could you try asking again in a moment?"
        
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
                return "Hmm, I don't have a specific answer for that one in my knowledge base. Could you try rephrasing it, or maybe ask about something else? I'm here to help however I can!"
                
        except Exception as e:
            print(f"❌ Error in FAQ matching: {e}")
            return "Oops! I ran into a little hiccup while searching for that answer. Could you give it another try? I promise I'm usually better at this!"
    
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
