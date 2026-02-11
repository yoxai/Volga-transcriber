# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies

```bash
# Install FFmpeg (required for audio conversion)
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Install Python packages
pip install -r requirements.txt
```

### 2. Run the API Server

```bash
python api.py

# Server starts at http://localhost:8000
```

### 3. Test with Sample Audio

**Using curl:**

```bash
# Upload an audio file
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@your_audio.mp3"

# Response: {"job_id": "abc-123", "status": "pending"}

# Check status
curl "http://localhost:8000/jobs/abc-123"
```

**Using Python:**

```python
import requests

# Upload
with open('audio.mp3', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/transcribe',
        files={'file': f}
    )
    job = response.json()

# Check status
status = requests.get(
    f"http://localhost:8000/jobs/{job['job_id']}"
).json()

print(status['result']['transcript'])
```

### 4. View API Documentation

Open browser: http://localhost:8000/docs

Interactive API documentation with Swagger UI.

## Docker Setup

```bash
# Build and run
docker-compose up --build

# API available at http://localhost:8000
```

## Example Output

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": {
    "transcript": "Hello world, this is a test transcription.",
    "segments": [
      {
        "segment_id": 0,
        "start_time": 0.0,
        "end_time": 3.5,
        "text": "Hello world, this is a test transcription.",
        "confidence": "high"
      }
    ],
    "total_duration": 3.5,
    "num_segments": 1
  }
}
```

## Troubleshooting

**Error: FFmpeg not found**
- Install FFmpeg as shown in step 1

**Error: Module not found**
- Run: `pip install -r requirements.txt`

**Error: Port 8000 already in use**
- Change port: `uvicorn api:app --port 8001`

## Next Steps

- Read [README.md](README.md) for full documentation
- Read [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) for system architecture
- Check [test_transcription.py](test_transcription.py) for examples
