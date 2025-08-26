#!/usr/bin/env python3
"""
Mock Scheduler Module for AI Interview Agent
Provides scheduling functionality with time slot management and booking logic.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import uuid
import json
import os

class MockScheduler:
    """
    Mock scheduling system for interview sessions.
    Manages available time slots, bookings, and scheduling logic.
    """
    
    def __init__(self, db_path: str = "interviews.db"):
        """
        Initialize the mock scheduler.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_scheduler_db()
        self._generate_default_slots()
    
    def init_scheduler_db(self) -> None:
        """Initialize the scheduler database tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create scheduled_sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scheduled_sessions (
                        session_id TEXT PRIMARY KEY,
                        candidate_name TEXT NOT NULL,
                        candidate_email TEXT,
                        candidate_phone TEXT,
                        scheduled_time TEXT NOT NULL,
                        status TEXT DEFAULT 'confirmed',
                        created_at TEXT NOT NULL,
                        reminder_sent BOOLEAN DEFAULT FALSE,
                        notes TEXT
                    )
                ''')
                
                # Create available_slots table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS available_slots (
                        slot_id TEXT PRIMARY KEY,
                        start_time TEXT NOT NULL,
                        end_time TEXT NOT NULL,
                        is_available BOOLEAN DEFAULT TRUE,
                        session_id TEXT,
                        created_at TEXT NOT NULL
                    )
                ''')
                
                conn.commit()
                print(f"✓ Scheduler database initialized successfully")
                
        except sqlite3.Error as e:
            print(f"❌ Scheduler database initialization error: {e}")
            raise
    
    def _generate_default_slots(self) -> None:
        """Generate default available time slots for the next 7 days."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if slots already exist
                cursor.execute('SELECT COUNT(*) FROM available_slots')
                if cursor.fetchone()[0] > 0:
                    return  # Slots already exist
                
                # Generate slots for next 7 days
                base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
                
                for day in range(7):
                    current_date = base_date + timedelta(days=day)
                    
                    # Skip weekends (Saturday=5, Sunday=6)
                    if current_date.weekday() >= 5:
                        continue
                    
                    # Generate slots from 9 AM to 5 PM, 1-hour intervals
                    for hour in range(9, 17):
                        slot_start = current_date.replace(hour=hour, minute=0)
                        slot_end = slot_start + timedelta(hours=1)
                        
                        slot_id = str(uuid.uuid4())
                        cursor.execute('''
                            INSERT INTO available_slots (slot_id, start_time, end_time, is_available, created_at)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (slot_id, slot_start.isoformat(), slot_end.isoformat(), True, datetime.now().isoformat()))
                
                conn.commit()
                print(f"✓ Generated default time slots for next 7 days")
                
        except sqlite3.Error as e:
            print(f"❌ Error generating default slots: {e}")
    
    def get_available_slots(self, days_ahead: int = 7) -> List[Dict]:
        """
        Get available time slots for the specified number of days.
        
        Args:
            days_ahead (int): Number of days to look ahead
            
        Returns:
            List[Dict]: List of available time slots
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get slots within the specified range
                end_date = datetime.now() + timedelta(days=days_ahead)
                
                cursor.execute('''
                    SELECT slot_id, start_time, end_time
                    FROM available_slots
                    WHERE is_available = TRUE 
                    AND start_time > ?
                    AND start_time < ?
                    ORDER BY start_time
                ''', (datetime.now().isoformat(), end_date.isoformat()))
                
                slots = []
                for row in cursor.fetchall():
                    slots.append({
                        'slot_id': row[0],
                        'start_time': row[1],
                        'end_time': row[2],
                        'formatted_time': self._format_slot_time(row[1])
                    })
                
                return slots
                
        except sqlite3.Error as e:
            print(f"❌ Error retrieving available slots: {e}")
            return []
    
    def _format_slot_time(self, iso_time: str) -> str:
        """Format ISO time string to human-readable format."""
        try:
            dt = datetime.fromisoformat(iso_time)
            return dt.strftime("%A, %B %d at %I:%M %p")
        except:
            return iso_time
    
    def book_session(self, candidate_name: str, candidate_email: str = "", 
                    candidate_phone: str = "", slot_id: str = None, 
                    preferred_time: str = None, notes: str = "") -> Optional[str]:
        """
        Book an interview session.
        
        Args:
            candidate_name (str): Name of the candidate
            candidate_email (str): Email of the candidate
            candidate_phone (str): Phone number of the candidate
            slot_id (str): Specific slot ID to book
            preferred_time (str): Preferred time (if slot_id not provided)
            notes (str): Additional notes
            
        Returns:
            str: Session ID if successful, None otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Generate session ID
                session_id = str(uuid.uuid4())
                
                # Determine the time slot
                if slot_id:
                    # Use specific slot
                    cursor.execute('''
                        SELECT start_time, end_time 
                        FROM available_slots 
                        WHERE slot_id = ? AND is_available = TRUE
                    ''', (slot_id,))
                    slot = cursor.fetchone()
                    
                    if not slot:
                        print(f"❌ Slot {slot_id} is not available")
                        return None
                    
                    scheduled_time = slot[0]
                    
                    # Mark slot as unavailable
                    cursor.execute('''
                        UPDATE available_slots 
                        SET is_available = FALSE, session_id = ?
                        WHERE slot_id = ?
                    ''', (session_id, slot_id))
                    
                else:
                    # Find next available slot
                    cursor.execute('''
                        SELECT slot_id, start_time 
                        FROM available_slots 
                        WHERE is_available = TRUE 
                        AND start_time > ?
                        ORDER BY start_time 
                        LIMIT 1
                    ''', (datetime.now().isoformat(),))
                    
                    slot = cursor.fetchone()
                    if not slot:
                        print("❌ No available slots found")
                        return None
                    
                    slot_id = slot[0]
                    scheduled_time = slot[1]
                    
                    # Mark slot as unavailable
                    cursor.execute('''
                        UPDATE available_slots 
                        SET is_available = FALSE, session_id = ?
                        WHERE slot_id = ?
                    ''', (session_id, slot_id))
                
                # Create scheduled session
                cursor.execute('''
                    INSERT INTO scheduled_sessions 
                    (session_id, candidate_name, candidate_email, candidate_phone, 
                     scheduled_time, status, created_at, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (session_id, candidate_name, candidate_email, candidate_phone,
                     scheduled_time, 'confirmed', datetime.now().isoformat(), notes))
                
                conn.commit()
                print(f"✓ Session booked successfully: {session_id}")
                return session_id
                
        except sqlite3.Error as e:
            print(f"❌ Error booking session: {e}")
            return None
    
    def get_scheduled_sessions(self, status: str = None) -> List[Dict]:
        """
        Get all scheduled sessions, optionally filtered by status.
        
        Args:
            status (str): Filter by status ('confirmed', 'completed', 'cancelled')
            
        Returns:
            List[Dict]: List of scheduled sessions
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if status:
                    cursor.execute('''
                        SELECT session_id, candidate_name, candidate_email, 
                               scheduled_time, status, created_at, notes
                        FROM scheduled_sessions
                        WHERE status = ?
                        ORDER BY scheduled_time
                    ''', (status,))
                else:
                    cursor.execute('''
                        SELECT session_id, candidate_name, candidate_email, 
                               scheduled_time, status, created_at, notes
                        FROM scheduled_sessions
                        ORDER BY scheduled_time
                    ''')
                
                sessions = []
                for row in cursor.fetchall():
                    sessions.append({
                        'session_id': row[0],
                        'candidate_name': row[1],
                        'candidate_email': row[2],
                        'scheduled_time': row[3],
                        'status': row[4],
                        'created_at': row[5],
                        'notes': row[6],
                        'formatted_time': self._format_slot_time(row[3])
                    })
                
                return sessions
                
        except sqlite3.Error as e:
            print(f"❌ Error retrieving scheduled sessions: {e}")
            return []
    
    def cancel_session(self, session_id: str) -> bool:
        """
        Cancel a scheduled session.
        
        Args:
            session_id (str): Session ID to cancel
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Update session status
                cursor.execute('''
                    UPDATE scheduled_sessions 
                    SET status = 'cancelled'
                    WHERE session_id = ?
                ''', (session_id,))
                
                # Free up the time slot
                cursor.execute('''
                    UPDATE available_slots 
                    SET is_available = TRUE, session_id = NULL
                    WHERE session_id = ?
                ''', (session_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"✓ Session cancelled successfully: {session_id}")
                    return True
                else:
                    print(f"⚠ Session not found: {session_id}")
                    return False
                
        except sqlite3.Error as e:
            print(f"❌ Error cancelling session: {e}")
            return False
    
    def complete_session(self, session_id: str) -> bool:
        """
        Mark a session as completed.
        
        Args:
            session_id (str): Session ID to mark as completed
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE scheduled_sessions 
                    SET status = 'completed'
                    WHERE session_id = ?
                ''', (session_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"✓ Session marked as completed: {session_id}")
                    return True
                else:
                    print(f"⚠ Session not found: {session_id}")
                    return False
                
        except sqlite3.Error as e:
            print(f"❌ Error completing session: {e}")
            return False
    
    def get_session_details(self, session_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific session.
        
        Args:
            session_id (str): Session ID to retrieve
            
        Returns:
            Dict: Session details or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT session_id, candidate_name, candidate_email, 
                           candidate_phone, scheduled_time, status, 
                           created_at, reminder_sent, notes
                    FROM scheduled_sessions
                    WHERE session_id = ?
                ''', (session_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'session_id': row[0],
                        'candidate_name': row[1],
                        'candidate_email': row[2],
                        'candidate_phone': row[3],
                        'scheduled_time': row[4],
                        'status': row[5],
                        'created_at': row[6],
                        'reminder_sent': row[7],
                        'notes': row[8],
                        'formatted_time': self._format_slot_time(row[4])
                    }
                return None
                
        except sqlite3.Error as e:
            print(f"❌ Error retrieving session details: {e}")
            return None
    
    def get_upcoming_sessions(self, hours_ahead: int = 24) -> List[Dict]:
        """
        Get sessions scheduled within the next specified hours.
        
        Args:
            hours_ahead (int): Number of hours to look ahead
            
        Returns:
            List[Dict]: List of upcoming sessions
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                end_time = datetime.now() + timedelta(hours=hours_ahead)
                
                cursor.execute('''
                    SELECT session_id, candidate_name, candidate_email, 
                           scheduled_time, status, notes
                    FROM scheduled_sessions
                    WHERE scheduled_time > ? 
                    AND scheduled_time < ?
                    AND status = 'confirmed'
                    ORDER BY scheduled_time
                ''', (datetime.now().isoformat(), end_time.isoformat()))
                
                sessions = []
                for row in cursor.fetchall():
                    sessions.append({
                        'session_id': row[0],
                        'candidate_name': row[1],
                        'candidate_email': row[2],
                        'scheduled_time': row[3],
                        'status': row[4],
                        'notes': row[5],
                        'formatted_time': self._format_slot_time(row[3])
                    })
                
                return sessions
                
        except sqlite3.Error as e:
            print(f"❌ Error retrieving upcoming sessions: {e}")
            return []

def main():
    """Test the mock scheduler functionality."""
    print("🧪 Testing Mock Scheduler...")
    print("=" * 50)
    
    # Initialize scheduler
    scheduler = MockScheduler()
    
    # Get available slots
    print("\n📅 Available time slots:")
    slots = scheduler.get_available_slots()
    for i, slot in enumerate(slots[:5], 1):  # Show first 5 slots
        print(f"  {i}. {slot['formatted_time']}")
    
    # Book a test session
    print(f"\n📝 Booking test session...")
    session_id = scheduler.book_session(
        candidate_name="John Doe",
        candidate_email="john.doe@example.com",
        candidate_phone="555-1234",
        notes="Test interview session"
    )
    
    if session_id:
        print(f"✓ Test session booked: {session_id}")
        
        # Get session details
        print(f"\n📋 Session details:")
        details = scheduler.get_session_details(session_id)
        if details:
            print(f"  Name: {details['candidate_name']}")
            print(f"  Email: {details['candidate_email']}")
            print(f"  Time: {details['formatted_time']}")
            print(f"  Status: {details['status']}")
        
        # Get upcoming sessions
        print(f"\n⏰ Upcoming sessions:")
        upcoming = scheduler.get_upcoming_sessions()
        for session in upcoming:
            print(f"  - {session['candidate_name']} at {session['formatted_time']}")
        
        # Clean up test session
        print(f"\n🧹 Cleaning up test session...")
        scheduler.cancel_session(session_id)
        
        print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    main()
