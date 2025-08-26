# Interview Scheduler

Automated interview scheduling system for the AI Interview Agent. Provides time slot management, booking logic, and session tracking.

## Features

### Core Functionality
- **Time Slot Management**: Automatically generates available interview slots (9 AM - 5 PM, weekdays)
- **Session Booking**: Book interviews with candidate information
- **Status Tracking**: Track sessions as confirmed, completed, or cancelled
- **Conflict Prevention**: Prevents double-booking of time slots
- **Database Integration**: Stores all scheduling data in SQLite database

### Interface Options
- **Voice Interface**: Schedule interviews through voice commands
- **Web Interface**: Streamlit-based booking interface
- **Command Line Interface**: Direct scheduling via CLI

## Usage

### Voice Interface
Run the main interview agent:

```bash
python main.py
```

Then speak:
- "Schedule" - to schedule an interview
- "Interview" - to start immediate interview  
- "View sessions" - to see scheduled sessions

### Web Interface
Access the scheduling interface through Streamlit:

```bash
streamlit run streamlit_app.py
```

Navigate to the "Schedule" section to book interviews.

### Programmatic Usage
Use the MockScheduler class directly:

```python
from scheduler import MockScheduler

# Initialize scheduler
scheduler = MockScheduler()

# Get available slots
slots = scheduler.get_available_slots(days_ahead=7)

# Book a session
session_id = scheduler.book_session(
    candidate_name="Jane Smith",
    candidate_email="jane@example.com",
    candidate_phone="555-1234",
    slot_id=slots[0]['slot_id']
)

# Get scheduled sessions
sessions = scheduler.get_scheduled_sessions()
```

## Database Schema

The scheduler creates two tables in `interviews.db`:

### `scheduled_sessions`
- `session_id` (TEXT, PRIMARY KEY)
- `candidate_name` (TEXT, NOT NULL)
- `candidate_email` (TEXT)
- `candidate_phone` (TEXT)
- `scheduled_time` (TEXT, NOT NULL)
- `status` (TEXT, DEFAULT 'confirmed')
- `created_at` (TEXT, NOT NULL)
- `reminder_sent` (BOOLEAN, DEFAULT FALSE)
- `notes` (TEXT)

### `available_slots`
- `slot_id` (TEXT, PRIMARY KEY)
- `start_time` (TEXT, NOT NULL)
- `end_time` (TEXT, NOT NULL)
- `is_available` (BOOLEAN, DEFAULT TRUE)
- `session_id` (TEXT)
- `created_at` (TEXT, NOT NULL)

## Time Slot Generation

The scheduler automatically generates time slots with these rules:
- **Days**: Monday through Friday (excludes weekends)
- **Hours**: 9 AM to 5 PM (8 slots per day)
- **Duration**: 1 hour per slot
- **Range**: Next 7 days from initialization
- **Format**: ISO 8601 timestamps

## Session Statuses

- **confirmed**: Session is booked and confirmed
- **completed**: Interview has been conducted
- **cancelled**: Session was cancelled (slot becomes available again)

## Integration with Main Agent

The scheduler is fully integrated with the main interview agent:

1. **Menu System**: Main agent offers 3 options including scheduling
2. **Voice Interface**: Complete voice-based scheduling workflow
3. **Data Persistence**: All scheduled sessions stored in database
4. **Session Management**: View and manage sessions through voice commands

## Quick Start

1. **Start the agent**: `python main.py`
2. **Choose scheduling**: Say "schedule" or select option 1
3. **Provide information**: Enter name, email, and phone
4. **Select time slot**: Choose from available options
5. **Confirmation**: Receive confirmation of scheduled interview
6. **View sessions**: Use option 3 to see all scheduled sessions

## Error Handling

The scheduler includes comprehensive error handling:
- **Slot conflicts**: Prevents double-booking
- **Invalid inputs**: Graceful handling of malformed data
- **Database errors**: Proper error messages and recovery
- **Voice recognition**: Fallback options for unclear speech

## Future Enhancements

Potential improvements for the scheduler:
- **Email notifications**: Send confirmation and reminder emails
- **Calendar integration**: Sync with Google Calendar or Outlook
- **Recurring slots**: Support for regular interview times
- **Multiple interviewers**: Support for different interviewer schedules
- **Time zone support**: Handle different time zones
- **Web interface**: Enhanced dashboard for scheduling management

## Testing

Test the scheduler functionality:

```bash
# Test the scheduler module
python scheduler.py

# Test via main interface
python main.py
```

## Files

- `scheduler.py` - Core scheduling functionality
- `SCHEDULER_README.md` - This documentation

## Dependencies

No additional dependencies required - uses existing SQLite database and standard Python libraries.
