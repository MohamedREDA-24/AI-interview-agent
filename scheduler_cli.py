#!/usr/bin/env python3
"""
Command Line Interface for Mock Scheduler
Provides easy management of interview scheduling from the command line.
"""

import argparse
import sys
from datetime import datetime
from scheduler import MockScheduler

def main():
    """Main CLI function for scheduler management."""
    parser = argparse.ArgumentParser(description='Mock Interview Scheduler CLI')
    parser.add_argument('command', choices=['slots', 'book', 'list', 'cancel', 'complete', 'details', 'upcoming'],
                       help='Command to execute')
    
    # Optional arguments
    parser.add_argument('--name', help='Candidate name for booking')
    parser.add_argument('--email', help='Candidate email for booking')
    parser.add_argument('--phone', help='Candidate phone for booking')
    parser.add_argument('--session-id', help='Session ID for operations')
    parser.add_argument('--days', type=int, default=7, help='Number of days to look ahead for slots')
    parser.add_argument('--hours', type=int, default=24, help='Number of hours to look ahead for upcoming sessions')
    parser.add_argument('--status', choices=['confirmed', 'completed', 'cancelled'], 
                       help='Filter sessions by status')
    
    args = parser.parse_args()
    
    # Initialize scheduler
    try:
        scheduler = MockScheduler()
    except Exception as e:
        print(f"❌ Failed to initialize scheduler: {e}")
        sys.exit(1)
    
    # Execute commands
    if args.command == 'slots':
        show_available_slots(scheduler, args.days)
    elif args.command == 'book':
        book_session(scheduler, args)
    elif args.command == 'list':
        list_sessions(scheduler, args.status)
    elif args.command == 'cancel':
        cancel_session(scheduler, args.session_id)
    elif args.command == 'complete':
        complete_session(scheduler, args.session_id)
    elif args.command == 'details':
        show_session_details(scheduler, args.session_id)
    elif args.command == 'upcoming':
        show_upcoming_sessions(scheduler, args.hours)

def show_available_slots(scheduler, days_ahead):
    """Show available time slots."""
    print(f"📅 Available interview slots (next {days_ahead} days):")
    print("=" * 60)
    
    slots = scheduler.get_available_slots(days_ahead)
    
    if not slots:
        print("❌ No available slots found")
        return
    
    for i, slot in enumerate(slots, 1):
        print(f"{i:2d}. {slot['formatted_time']}")
    
    print(f"\nTotal available slots: {len(slots)}")

def book_session(scheduler, args):
    """Book a new interview session."""
    print("📝 Booking new interview session...")
    print("=" * 60)
    
    # Get candidate information
    name = args.name
    email = args.email
    phone = args.phone
    
    if not name:
        name = input("Candidate name: ").strip()
        if not name:
            print("❌ Candidate name is required")
            return
    
    if not email:
        email = input("Candidate email (optional): ").strip()
    
    if not phone:
        phone = input("Candidate phone (optional): ").strip()
    
    # Show available slots
    slots = scheduler.get_available_slots()
    if not slots:
        print("❌ No available slots found")
        return
    
    print("\nAvailable slots:")
    for i, slot in enumerate(slots[:10], 1):  # Show first 10 slots
        print(f"{i:2d}. {slot['formatted_time']}")
    
    # Get slot choice
    try:
        choice = int(input(f"\nSelect slot (1-{min(10, len(slots))}): ")) - 1
        if 0 <= choice < len(slots):
            selected_slot = slots[choice]
        else:
            print("❌ Invalid choice")
            return
    except ValueError:
        print("❌ Invalid input")
        return
    
    # Book the session
    session_id = scheduler.book_session(
        candidate_name=name,
        candidate_email=email,
        candidate_phone=phone,
        slot_id=selected_slot['slot_id'],
        notes="Booked via CLI"
    )
    
    if session_id:
        print(f"✅ Interview booked successfully!")
        print(f"Session ID: {session_id}")
        print(f"Time: {selected_slot['formatted_time']}")
    else:
        print("❌ Failed to book interview")

def list_sessions(scheduler, status=None):
    """List all scheduled sessions."""
    print("📋 Scheduled interview sessions:")
    print("=" * 60)
    
    sessions = scheduler.get_scheduled_sessions(status)
    
    if not sessions:
        print("No scheduled sessions found.")
        return
    
    for session in sessions:
        print(f"Session ID: {session['session_id']}")
        print(f"Name: {session['candidate_name']}")
        print(f"Email: {session['candidate_email']}")
        print(f"Time: {session['formatted_time']}")
        print(f"Status: {session['status']}")
        print(f"Created: {session['created_at']}")
        if session['notes']:
            print(f"Notes: {session['notes']}")
        print("-" * 40)

def cancel_session(scheduler, session_id):
    """Cancel a scheduled session."""
    if not session_id:
        session_id = input("Session ID to cancel: ").strip()
    
    if not session_id:
        print("❌ Session ID is required")
        return
    
    print(f"🗑️  Cancelling session: {session_id}")
    
    if scheduler.cancel_session(session_id):
        print("✅ Session cancelled successfully")
    else:
        print("❌ Failed to cancel session")

def complete_session(scheduler, session_id):
    """Mark a session as completed."""
    if not session_id:
        session_id = input("Session ID to complete: ").strip()
    
    if not session_id:
        print("❌ Session ID is required")
        return
    
    print(f"✅ Marking session as completed: {session_id}")
    
    if scheduler.complete_session(session_id):
        print("✅ Session marked as completed")
    else:
        print("❌ Failed to complete session")

def show_session_details(scheduler, session_id):
    """Show detailed information about a session."""
    if not session_id:
        session_id = input("Session ID to view: ").strip()
    
    if not session_id:
        print("❌ Session ID is required")
        return
    
    print(f"📋 Session details: {session_id}")
    print("=" * 60)
    
    details = scheduler.get_session_details(session_id)
    
    if details:
        print(f"Session ID: {details['session_id']}")
        print(f"Candidate Name: {details['candidate_name']}")
        print(f"Candidate Email: {details['candidate_email']}")
        print(f"Candidate Phone: {details['candidate_phone']}")
        print(f"Scheduled Time: {details['formatted_time']}")
        print(f"Status: {details['status']}")
        print(f"Created At: {details['created_at']}")
        print(f"Reminder Sent: {details['reminder_sent']}")
        if details['notes']:
            print(f"Notes: {details['notes']}")
    else:
        print("❌ Session not found")

def show_upcoming_sessions(scheduler, hours_ahead):
    """Show upcoming sessions within specified hours."""
    print(f"⏰ Upcoming sessions (next {hours_ahead} hours):")
    print("=" * 60)
    
    sessions = scheduler.get_upcoming_sessions(hours_ahead)
    
    if not sessions:
        print("No upcoming sessions found.")
        return
    
    for session in sessions:
        print(f"Session ID: {session['session_id']}")
        print(f"Name: {session['candidate_name']}")
        print(f"Email: {session['candidate_email']}")
        print(f"Time: {session['formatted_time']}")
        print(f"Status: {session['status']}")
        if session['notes']:
            print(f"Notes: {session['notes']}")
        print("-" * 40)

if __name__ == "__main__":
    main()
