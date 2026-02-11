# User Manual: Transcription Service

This guide explains how to install and run the Transcription Service on your computer.

## 1. Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+**: [Download Python](https://www.python.org/downloads/)
- **FFmpeg**: Required for audio processing.
  - **Windows**: `choco install ffmpeg` (Run PowerShell as Admin)
  - **Mac**: `brew install ffmpeg`
  - **Linux**: `sudo apt install ffmpeg`

## 2. Installation

1. **Download the Code**: Clone the repository or download the ZIP file.
2. **Open Terminal**: Navigate to the project folder.

    ```bash
    cd transcription-pipeline
    ```

3. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

    *(Note: This installs all necessary libraries like FastAPI, pydub, and speech_recognition.)*

## 3. Running the Service

### Option A: Running Locally (Python)

To start the server, run:

```bash
python api.py
```

You should see output indicating the server is running at `http://localhost:8000`.

### Option B: Running with Docker (Recommended for Production)

Docker allows you to run the application in an isolated container without installing Python or FFmpeg on your machine.

1. **Build and Run**:

    ```bash
    docker-compose up --build
    ```

2. **Access**: The API will be available at `http://localhost:8000`.

## 4. How to Use

### Option A: Web Interface (Easiest)

1. Open your browser and go to: [http://localhost:8000/docs](http://localhost:8000/docs)
2. Click on **POST /transcribe**.
3. Click **Try it out**.
4. Upload an audio file (MP3, WAV, etc.).
5. Click **Execute**.
6. Copy the `job_id` from the response.
7. Go to **GET /jobs/{job_id}**, paste the ID, and click **Execute** to see your transcript!

### Option B: Command Line (Curl)

**Upload a file:**

```bash
curl -X POST "http://localhost:8000/transcribe" -F "file=@your_audio.mp3"
```

**Check status:**

```bash
curl "http://localhost:8000/jobs/<your_job_id>"
```

## 5. Troubleshooting

- **"FFmpeg not found"**: Ensure FFmpeg is installed and added to your system PATH.
- **"Module not found"**: Run `pip install -r requirements.txt` again.
- **Server errors**: Check the terminal output for error messages.
