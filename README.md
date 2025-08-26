# AI Interview Agent

A voice-enabled AI interview system powered by Google Gemini for automated candidate screening and evaluation.

## Features

- **Voice Interface**: Speech-to-text and text-to-speech capabilities for natural conversations
- **AI-Powered**: Integration with Google Gemini for intelligent responses and analysis
- **Interview Management**: Structured 5-question interview flow with automated evaluation
- **FAQ System**: Semantic search for answering candidate questions
- **Session Logging**: SQLite database for storing interview transcripts and summaries
- **Scheduling System**: Book and manage interview appointments
- **Web Interface**: Modern Streamlit-based UI for easy interaction

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Google API key:**
   - Create a `.env` file in the project root
   - Add your Google API key: `GOOGLE_API_KEY=your_api_key_here`
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

3. **Audio setup (optional for voice mode):**
   - Ensure microphone and speakers are working
   - Check system volume settings

## Usage

### Web Interface (Recommended)
```bash
streamlit run streamlit_app.py
```
Access the application at `http://localhost:8501`

### Command Line Interface
```bash
python main.py
```
Run the voice-based interview system directly

## Interview Questions

1. What is your full name and background?
2. Why are you interested in joining the program?
3. What's your experience with data science or AI?
4. What are your short-term and long-term goals?
5. Are you ready to start immediately? If not, when?

## Project Structure

- `main.py` - Command-line interview agent with voice capabilities
- `streamlit_app.py` - Web-based user interface
- `faq.py` - FAQ system using semantic similarity
- `summarizer.py` - AI-powered interview summarization
- `logger.py` - Session logging and database management
- `scheduler.py` - Interview scheduling system
- `interviews.db` - SQLite database for session storage

## Dependencies

- **Core AI**: `google-generativeai` for Gemini integration
- **Voice**: `pyttsx3`, `SpeechRecognition`, `PyAudio`
- **NLP**: `sentence-transformers`, `scikit-learn`
- **Web UI**: `streamlit`
- **Utilities**: `python-dotenv`

## Troubleshooting

### Audio Issues
1. Check microphone and speaker connections
2. Verify system volume settings
3. Ensure microphone permissions are granted
4. Use text-only mode as fallback

### API Issues
1. Verify `.env` file contains valid `GOOGLE_API_KEY`
2. Check internet connection
3. Ensure API key has proper permissions

### Voice Recognition Issues
1. Speak clearly and avoid background noise
2. Check microphone permissions
3. Try text-only mode as alternative

## Future Enhancements

- Custom interview question sets
- Multi-language support
- Advanced analytics and reporting
- Integration with HR systems
- Real-time transcription
- Video interview support

## Requirements

- Python 3.7+
- Windows/Mac/Linux
- Internet connection
- Microphone and speakers (for voice features)
- Google API key
- Approximately 2GB RAM for optimal performance

## Getting Started

Run the web interface:
```bash
streamlit run streamlit_app.py
```

Or use the command line:
```bash
python main.py
```