import sqlite3
import uuid
from datetime import datetime
from typing import Optional
import os

class InterviewLogger:
    """Logging and session memory module for AI interview agent."""
    
    def __init__(self, db_path: str = "interviews.db"):
        """
        Initialize the InterviewLogger.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_db()
    
    def init_db(self) -> None:
        """
        Initialize the database and create the sessions table if it doesn't exist.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        transcript TEXT NOT NULL,
                        summary TEXT NOT NULL
                    )
                ''')
                
                conn.commit()
                print(f"✓ Database initialized successfully: {self.db_path}")
                
        except sqlite3.Error as e:
            print(f"❌ Database initialization error: {e}")
            raise
    
    def save_session(self, session_id: str, transcript: str, summary: str) -> bool:
        """
        Save an interview session to the database.
        
        Args:
            session_id (str): Unique identifier for the session
            transcript (str): Full transcript of the interview
            summary (str): AI-generated summary of the interview
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert session data
                cursor.execute('''
                    INSERT INTO sessions (session_id, timestamp, transcript, summary)
                    VALUES (?, ?, ?, ?)
                ''', (session_id, datetime.now().isoformat(), transcript, summary))
                
                conn.commit()
                print(f"✓ Session saved successfully: {session_id}")
                return True
                
        except sqlite3.Error as e:
            print(f"❌ Error saving session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """
        Retrieve a specific session from the database.
        
        Args:
            session_id (str): Unique identifier for the session
            
        Returns:
            dict: Session data or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT session_id, timestamp, transcript, summary
                    FROM sessions
                    WHERE session_id = ?
                ''', (session_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'session_id': row[0],
                        'timestamp': row[1],
                        'transcript': row[2],
                        'summary': row[3]
                    }
                return None
                
        except sqlite3.Error as e:
            print(f"❌ Error retrieving session: {e}")
            return None
    
    def get_all_sessions(self) -> list:
        """
        Retrieve all sessions from the database.
        
        Returns:
            list: List of all session dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT session_id, timestamp, transcript, summary
                    FROM sessions
                    ORDER BY timestamp DESC
                ''')
                
                rows = cursor.fetchall()
                sessions = []
                for row in rows:
                    sessions.append({
                        'session_id': row[0],
                        'timestamp': row[1],
                        'transcript': row[2],
                        'summary': row[3]
                    })
                
                return sessions
                
        except sqlite3.Error as e:
            print(f"❌ Error retrieving sessions: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a specific session from the database.
        
        Args:
            session_id (str): Unique identifier for the session
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"✓ Session deleted successfully: {session_id}")
                    return True
                else:
                    print(f"⚠ Session not found: {session_id}")
                    return False
                
        except sqlite3.Error as e:
            print(f"❌ Error deleting session: {e}")
            return False
    
    def get_session_count(self) -> int:
        """
        Get the total number of sessions in the database.
        
        Returns:
            int: Number of sessions
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM sessions')
                count = cursor.fetchone()[0]
                
                return count
                
        except sqlite3.Error as e:
            print(f"❌ Error counting sessions: {e}")
            return 0

def generate_session_id() -> str:
    """
    Generate a unique session ID using UUID.
    
    Returns:
        str: Unique session identifier
    """
    return str(uuid.uuid4())

# Test block
if __name__ == "__main__":
    print("🧪 Testing InterviewLogger...")
    print("=" * 50)
    
    # Initialize logger
    logger = InterviewLogger()
    
    # Generate test data
    test_session_id = generate_session_id()
    test_transcript = "This is a test interview transcript with sample questions and answers."
    test_summary = "Test candidate showed good communication skills and relevant experience."
    
    # Save test session
    print(f"\n📝 Saving test session: {test_session_id}")
    success = logger.save_session(test_session_id, test_transcript, test_summary)
    
    if success:
        # Retrieve and display the session
        print("\n📖 Retrieving test session...")
        session = logger.get_session(test_session_id)
        
        if session:
            print("✓ Session retrieved successfully!")
            print(f"Session ID: {session['session_id']}")
            print(f"Timestamp: {session['timestamp']}")
            print(f"Transcript: {session['transcript']}")
            print(f"Summary: {session['summary']}")
        
        # Show session count
        count = logger.get_session_count()
        print(f"\n📊 Total sessions in database: {count}")
        
        # Clean up test session
        print(f"\n🧹 Cleaning up test session...")
        logger.delete_session(test_session_id)
        
        final_count = logger.get_session_count()
        print(f"📊 Final session count: {final_count}")
        
        print("\n✅ All tests completed successfully!")
    else:
        print("❌ Test failed - could not save session")
