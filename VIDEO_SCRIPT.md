# Video Explainer Script

**Target Length:** ~3-5 minutes
**Goal:** Demonstrate the Transcription Pipeline works and explain the key engineering decisions (Part 1 & 2 of the assessment).

## **1. Introduction (0:00 - 0:30)**

| **Show on Screen** | **Say (Summary)** |
| :--- | :--- |
| **VS Code (Project Root)**<br>Show the file structure in the sidebar. | "Hi, this is [Your Name]. This is my submitted solution for the Transcription Pipeline assessment." |
| **README.md (Top)**<br>Scroll briefly. | "I've built a production-ready audio transcription service using **Python** and **FastAPI**. It handles multiple audio formats, supports long files via chunking, and processes requests asynchronously." |

---

## **2. Architecture & Design (0:30 - 1:30)**

| **Show on Screen** | **Say (Summary)** |
| :--- | :--- |
| **README.md ("Architecture" Diagram)**<br>Highlight the diagram. | "The system architecture consists of a FastAPI server that handles HTTP requests and delegates long-running tasks to a background worker. This ensures the API remains responsive." |
| **README.md ("Design Decisions")**<br>Scroll to the "Design Decisions" section. | "For the system design questions in Part 2, I've documented my approach here. For example:<br>1. **Concurrent Uploads**: Handled via async background tasks (and allows scaling with message queues).<br>2. **Storage**: I propose using S3 for raw/processed audio and PostgreSQL for metadata/results." |

---

## **3. Code Walk-through (1:30 - 3:00)**

| **Show on Screen** | **Say (Summary)** |
| :--- | :--- |
| **`transcription_service.py`**<br>Open file. | "Let's look at the core logic in `TranscriptionService`." |
| **`chunk_audio_by_silence` method**<br>Highlight lines ~155-190. | "Handling long audio files was a key requirement. I implemented an intelligent chunking strategy that splits audio based on **silence detection** (`pydub`). This improves transcription accuracy versus arbitrary splitting." |
| **`convert_to_wav` method**<br>Highlight lines ~91-125. | "To handle different formats (MP3, WAV, etc.), I use `pydub` (backed by `ffmpeg`) to normalize everything to a standard 16kHz WAV format before processing." |
| **`transcribe` method**<br>Highlight the `try/except` block and timestamp loop. | "The `transcribe` method orchestrates the validation, conversion, chunking, and final transcription using `speech_recognition`. It also calculates precise timestamps for each segment." |
| **`api.py`**<br>Open file. | "The API layer uses FastAPI. The `/transcribe` endpoint accepts the file and returns a Job ID immediately, while `BackgroundTasks` handle the actual processing." |

---

## **4. Live Demo (3:00 - 4:30)**

| **Show on Screen** | **Say (Summary)** |
| :--- | :--- |
| **Terminal**<br>Run `python api.py` | "Now, let's see it in action. I'll start the server." |
| **Browser (Swagger UI)**<br>Go to `http://localhost:8000/docs` | "I'm using the auto-generated Swagger UI for testing." |
| **POST /transcribe**<br>Expand the endpoint.<br>Click **Try it out**.<br>Upload `sample.mp3` (or any file).<br>Click **Execute**. | "I'll upload a sample audio file. As you can see, I get an immediate response with a `job_id` and a `pending` status." |
| **Copy the `job_id`** | "I'll copy this Job ID to check the status." |
| **GET /jobs/{job_id}**<br>Expand endpoint.<br>Paste ID.<br>Click **Execute**. | "Now I'll query the job status..." |
| **Response Body (JSON)**<br>Scroll through the JSON. | "...and here is the result. The status is `completed`.<br>You can see the full `transcript` here.<br>And below, we have the `segments` array, where each sentence has a precise `start_time` and `end_time`." |

---

## **5. Conclusion (4:30 - End)**

| **Show on Screen** | **Say (Summary)** |
| :--- | :--- |
| **GitHub Repo** (if ready)<br>OR back to **README.md** | "The full source code, including Docker configuration and unit tests, is available in the Git repository linked in the submission.<br>Thank you for your time!" |
