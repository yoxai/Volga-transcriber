"""
REST API for Transcription Service
Provides HTTP endpoints for audio transcription with async processing and job management.
"""

from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
import uuid
import os
from datetime import datetime
import asyncio
from pathlib import Path
import aiofiles

from transcription_service import TranscriptionService

app = FastAPI(
    title="Audio Transcription API",
    description="Production-ready API for audio transcription with concurrent processing",
    version="1.0.0"
)

# Job storage (in production, use Redis or database)
transcription_jobs: Dict[str, Dict] = {}

# Service instance
transcription_service = TranscriptionService()

# Configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class TranscriptionJob(BaseModel):
    """Model for transcription job status"""
    job_id: str
    status: str  # pending, processing, completed, failed
    file_name: str
    created_at: str
    updated_at: str
    result: Optional[Dict] = None
    error: Optional[str] = None


class TranscriptionResponse(BaseModel):
    """Model for immediate API response"""
    job_id: str
    status: str
    message: str


async def save_upload_file(upload_file: UploadFile, destination: Path) -> None:
    """Save uploaded file asynchronously."""
    async with aiofiles.open(destination, 'wb') as out_file:
        content = await upload_file.read()
        await out_file.write(content)


def process_transcription_job(job_id: str, file_path: str) -> None:
    """
    Background task to process transcription.
    Updates job status in shared storage.
    """
    try:
        # Update status to processing
        transcription_jobs[job_id]['status'] = 'processing'
        transcription_jobs[job_id]['updated_at'] = datetime.now().isoformat()
        
        # Perform transcription
        result = transcription_service.transcribe(file_path)
        
        # Update job with result
        if result['status'] == 'success':
            transcription_jobs[job_id]['status'] = 'completed'
            transcription_jobs[job_id]['result'] = result
        else:
            transcription_jobs[job_id]['status'] = 'failed'
            transcription_jobs[job_id]['error'] = result.get('error', 'Unknown error')
        
        transcription_jobs[job_id]['updated_at'] = datetime.now().isoformat()
        
    except Exception as e:
        transcription_jobs[job_id]['status'] = 'failed'
        transcription_jobs[job_id]['error'] = str(e)
        transcription_jobs[job_id]['updated_at'] = datetime.now().isoformat()
    
    finally:
        # Cleanup uploaded file
        try:
            os.remove(file_path)
        except:
            pass


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Audio file to transcribe")
):
    """
    Upload an audio file for transcription.
    Processing happens asynchronously in the background.
    
    Returns a job_id to check transcription status.
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in transcription_service.SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: {file_ext}. Supported formats: {transcription_service.SUPPORTED_FORMATS}"
        )
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    file_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
    await save_upload_file(file, file_path)
    
    # Create job record
    transcription_jobs[job_id] = {
        'job_id': job_id,
        'status': 'pending',
        'file_name': file.filename,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'result': None,
        'error': None
    }
    
    # Queue background task
    background_tasks.add_task(process_transcription_job, job_id, str(file_path))
    
    return TranscriptionResponse(
        job_id=job_id,
        status='pending',
        message='Transcription job queued successfully'
    )


@app.get("/jobs/{job_id}", response_model=TranscriptionJob)
async def get_job_status(job_id: str):
    """
    Get the status and result of a transcription job.
    """
    if job_id not in transcription_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    return transcription_jobs[job_id]


@app.get("/jobs", response_model=List[TranscriptionJob])
async def list_jobs(
    status_filter: Optional[str] = None,
    limit: int = 10
):
    """
    List all transcription jobs with optional status filtering.
    """
    jobs = list(transcription_jobs.values())
    
    if status_filter:
        jobs = [job for job in jobs if job['status'] == status_filter]
    
    # Sort by created_at descending
    jobs.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jobs[:limit]


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a transcription job record.
    """
    if job_id not in transcription_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    del transcription_jobs[job_id]
    
    return {"message": f"Job {job_id} deleted successfully"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_jobs": len([j for j in transcription_jobs.values() if j['status'] == 'processing']),
        "total_jobs": len(transcription_jobs)
    }


@app.get("/")
async def root():
    """
    API documentation endpoint.
    """
    return {
        "message": "Audio Transcription API",
        "version": "1.0.0",
        "endpoints": {
            "POST /transcribe": "Submit audio file for transcription",
            "GET /jobs/{job_id}": "Get transcription job status",
            "GET /jobs": "List all jobs",
            "DELETE /jobs/{job_id}": "Delete a job",
            "GET /health": "Health check"
        },
        "supported_formats": list(transcription_service.SUPPORTED_FORMATS)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
