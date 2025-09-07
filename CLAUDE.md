# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI Judge Mock Trial System (AI 판사 모의재판 시스템) built with Streamlit for educational purposes at Geumcheon Middle School. The system enables students to conduct mock trials with AI-powered judgment.

## Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Environment Setup
Create a `.env` file with:
```
OPENAI_API_KEY=sk-your-key-here
```

## Architecture

### Core Components

1. **Main Application (`app.py`)**
   - Multi-tab Streamlit interface for mock trial management
   - Real-time audio transcription using OpenAI Whisper API
   - AI judgment generation using GPT models
   - Session state management for trial rounds and team data

2. **Key Features**
   - **Audio Recording**: Uses `audio_recorder_streamlit` for in-browser recording
   - **Speech-to-Text**: OpenAI Whisper API (`gpt-4o-transcribe`) for Korean/English transcription
   - **AI Judge**: GPT-5 model for generating educational judgments
   - **Data Persistence**: JSON export/import for trial records

3. **UI Structure**
   - Tab 1: Case setup and configuration
   - Tab 2: Round-by-round debate management with timer
   - Tab 3: AI judgment request and generation
   - Tab 4: Results analysis and scoring
   - Tab 5: Record management and data export

### Dependencies
- `streamlit`: Web application framework
- `openai`: API client for Whisper transcription and GPT models
- `audio-recorder-streamlit`: Browser-based audio recording widget
- `python-dotenv`: Environment variable management

## Key Considerations

- The app requires a valid OpenAI API key in the environment
- Audio transcription supports both Korean and English
- The system is designed for educational use in middle school mock trials
- Custom CSS provides a visually appealing interface with gradient backgrounds and card-based layouts