"""
Example usage of the Transcription API
"""

import requests
import time
import json

# API base URL
BASE_URL = "http://localhost:8000"


def upload_and_transcribe(audio_file_path):
    """
    Example: Upload an audio file and wait for transcription.
    """
    print(f"📤 Uploading: {audio_file_path}")
    
    # Upload file
    with open(audio_file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/transcribe", files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.text}")
        return
    
    job = response.json()
    job_id = job['job_id']
    print(f"✅ Job created: {job_id}")
    
    # Poll for completion
    print("⏳ Waiting for transcription...")
    
    while True:
        response = requests.get(f"{BASE_URL}/jobs/{job_id}")
        job_status = response.json()
        
        status = job_status['status']
        print(f"   Status: {status}")
        
        if status == 'completed':
            print("\n🎉 Transcription completed!\n")
            
            result = job_status['result']
            print(f"📝 Transcript:")
            print(f"   {result['transcript']}\n")
            
            print(f"📊 Details:")
            print(f"   Duration: {result['total_duration']:.2f}s")
            print(f"   Segments: {result['num_segments']}")
            print(f"   Processing time: {result['processing_time']:.2f}s\n")
            
            # Show segments with timestamps
            print("🕒 Timestamped Segments:")
            for seg in result['segments']:
                print(f"   [{seg['start_time']:.1f}s - {seg['end_time']:.1f}s] {seg['text']}")
            
            break
            
        elif status == 'failed':
            print(f"\n❌ Transcription failed: {job_status.get('error', 'Unknown error')}")
            break
        
        time.sleep(2)


def list_all_jobs():
    """
    Example: List all transcription jobs.
    """
    response = requests.get(f"{BASE_URL}/jobs")
    jobs = response.json()
    
    print(f"\n📋 Total jobs: {len(jobs)}\n")
    
    for job in jobs:
        print(f"Job ID: {job['job_id']}")
        print(f"  File: {job['file_name']}")
        print(f"  Status: {job['status']}")
        print(f"  Created: {job['created_at']}")
        print()


def check_health():
    """
    Example: Check API health.
    """
    response = requests.get(f"{BASE_URL}/health")
    health = response.json()
    
    print("\n💚 API Health Check")
    print(f"   Status: {health['status']}")
    print(f"   Active jobs: {health['active_jobs']}")
    print(f"   Total jobs: {health['total_jobs']}")
    print(f"   Timestamp: {health['timestamp']}\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Audio Transcription API - Example Usage")
    print("=" * 60)
    
    # Check API health
    check_health()
    
    # Example 1: Upload and transcribe
    # Replace with your actual audio file path
    audio_file = "sample_audio.mp3"
    
    import os
    if os.path.exists(audio_file):
        upload_and_transcribe(audio_file)
    else:
        print(f"⚠️  Sample file '{audio_file}' not found.")
        print("Please provide a valid audio file path to test.")
    
    # Example 2: List all jobs
    list_all_jobs()
