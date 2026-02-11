"""
Test suite for Transcription Service
"""

import pytest
import os
from pathlib import Path
from transcription_service import TranscriptionService

# Test data directory
TEST_DATA_DIR = Path("test_data")
TEST_DATA_DIR.mkdir(exist_ok=True)


@pytest.fixture
def service():
    """Create a TranscriptionService instance for testing."""
    return TranscriptionService(output_dir="test_transcriptions")


def test_validate_audio_file_success(service):
    """Test that valid audio files pass validation."""
    # Create a dummy WAV file
    test_file = TEST_DATA_DIR / "test.wav"
    test_file.touch()
    
    is_valid, error = service.validate_audio_file(str(test_file))
    
    assert is_valid is True
    assert error is None
    
    # Cleanup
    test_file.unlink()


def test_validate_audio_file_unsupported_format(service):
    """Test that unsupported formats fail validation."""
    test_file = TEST_DATA_DIR / "test.txt"
    test_file.touch()
    
    is_valid, error = service.validate_audio_file(str(test_file))
    
    assert is_valid is False
    assert "Unsupported format" in error
    
    # Cleanup
    test_file.unlink()


def test_validate_audio_file_not_found(service):
    """Test that non-existent files fail validation."""
    is_valid, error = service.validate_audio_file("nonexistent.wav")
    
    assert is_valid is False
    assert "File not found" in error


def test_supported_formats(service):
    """Test that all expected formats are supported."""
    expected_formats = {'.wav', '.mp3', '.m4a', '.flac', '.ogg'}
    
    assert expected_formats.issubset(service.SUPPORTED_FORMATS)


@pytest.mark.asyncio
async def test_api_health_check():
    """Test the API health check endpoint."""
    from httpx import AsyncClient
    from api import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_api_root():
    """Test the API root endpoint."""
    from httpx import AsyncClient
    from api import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "endpoints" in data
        assert "supported_formats" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
