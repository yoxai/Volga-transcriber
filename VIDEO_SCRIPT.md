# Video Explainer Script

**Target Length:** ~3-5 minutes
**Goal:** Demonstrate the Transcription Pipeline works and explain the key engineering decisions (Part 1 & 2 of the assessment).

## **1. Introduction (0:00 - 0:30)**

| **Show on Screen** | **Say (Summary)** |
| :--- | :--- |
| **VS Code (Project Root)** Show the file structure in the sidebar. | "Hi, this is [Your Name]. This is my submission for the Transcription Pipeline assessment." |
| **README.md (Top)** Scroll briefly. | "I've built a production-ready audio transcription service using **Python** and **FastAPI**. It handles multiple audio formats, supports long files via chunking, and processes requests asynchronously." |

---

## **2. Architecture & Design (0:30 - 1:30)**

| **Show on Screen** | **Say (Summary)** |
| :--- | :--- |
| **README.md ("Architecture" Diagram)** Highlight the diagram. | "The architecture consists of a FastAPI server that handles requests and delegates long-running tasks to a background worker. This ensures the API remains responsive." |
| **README.md ("Design Decisions" or "System Design")** Scroll to the "Design Decisions" section. | "For the system design questions in Part 2, I've documented my approach here. For example: 1. **Concurrent Uploads**: Handled via async background tasks. 2. **Storage**: I propose using S3 for raw/processed audio and PostgreSQL for metadata/results." |

---

## **3. Code Walk-through (1:30 - 3:00)**

| **Show on Screen** | **Say (Summary)** |
| :--- | :--- |
| **`transcription_service.py`** Open file. | "Let's look at the core logic in `TranscriptionService`." |
| **`chunk_audio_by_silence` method** Highlight lines ~155-190. | "Handling long audio files was a key requirement. I implemented an intelligent chunking strategy that splits audio based on **silence detection**. This improves accuracy over arbitrary splitting." |
| **`convert_to_wav` method** Highlight lines ~91-125. | "To handle different formats (MP3, WAV), I use `pydub` (backed by `ffmpeg`) to normalize everything to a standard 16kHz WAV format." |
| **`transcribe` method** Highlight the `try/except` block. | "The `transcribe` method orchestrates validation, conversion, chunking, and transcription. It also calculates precise timestamps for each segment." |
| **`api.py`** Open file. | "The API layer uses FastAPI. The `/transcribe` endpoint accepts the file and returns a Job ID immediately, while `BackgroundTasks` handle the processing." |

---

## **4. Live Demo (3:00 - 4:30)**

| **Show on Screen** | **Say (Summary)** |
| :--- | :--- |
| **Terminal** Run `python api.py` | "Now, let's see it in action. I'll start the server." |
| **Browser (Swagger UI)** Go to `http://localhost:8000/docs` | "I'm using the auto-generated Swagger UI for testing." |
| **POST /transcribe** Expand endpoint. Click **Try it out**. Upload `sample.mp3`. Click **Execute**. | "I'll upload a sample audio file. I get an immediate response with a `job_id` and a `pending` status." |
| **Copy the `job_id`** | "I'll copy this Job ID to check the status." |
| **GET /jobs/{job_id}** Expand endpoint. Paste ID. Click **Execute**. | "Now I'll query the job status..." |
| **Response Body (JSON)** Scroll through the JSON. | "...and here is the result. status: `completed`. You can see the full `transcript` here, and the `segments` array with precise `start_time` and `end_time`." |

---

## **5. Conclusion (4:30 - End)**

| **Show on Screen** | **Say (Summary)** |
| :--- | :--- |
| **User Manual** or **Repo** | "The code is Docker-ready and includes a User Manual for easy setup. Thank you for your time!" |
