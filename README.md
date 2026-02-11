# Audio Transcription Pipeline

A production-ready service that transcribes audio files into text with precise timestamps.

## 🚀 Quick Links

- **[User Manual](USER_MANUAL.md)**: Easy step-by-step guide to run the service.
- **[Developer Guide](DEVELOPER_GUIDE.md)**: Technical architecture, API specs, and design decisions.

## ✨ Features

- **Multi-Format**: Supports MP3, WAV, M4A, FLAC, OGG.
- **Detailed Output**: Provides full transcript + timestamped segments.
- **Scalable**: Handles long files via intelligent chunking.
- **Async API**: Non-blocking requests for better performance.

## 🛠️ Quick Start (Running Locally)

1. **Install**:

    ```bash
    pip install -r requirements.txt
    ```

2. **Run**:

    ```bash
    python api.py
    ```

3. **Transcribe**:
    - **Open**: `http://localhost:8000/docs`
    - **Upload**: Your audio file.
    - **Get Result**: Use the Job ID to fetch your transcript.

For detailed instructions, see the [User Manual](USER_MANUAL.md).

## 📝 Assessment Submission

This repository contains the full source code for the "Transcription Pipeline" assessment.

- **Part 1 (Code)**: Implemented in `transcription_service.py` and `api.py`.
- **Part 2 (Design)**: Answers are in `DEVELOPER_GUIDE.md`.
