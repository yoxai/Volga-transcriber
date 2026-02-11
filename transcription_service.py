"""
Transcription Service
A production-ready audio transcription pipeline with chunking, format conversion, and error handling.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib

# Audio processing
from pydub import AudioSegment
from pydub.silence import split_on_silence

# Speech recognition
import speech_recognition as sr

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TranscriptionService:
    """
    Main transcription service that handles audio file processing and transcription.
    """
    
    # Supported audio formats
    SUPPORTED_FORMATS = {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac', '.wma'}
    
    # Configuration
    CHUNK_LENGTH_MS = 60000  # 60 seconds per chunk
    MAX_FILE_SIZE_MB = 500
    SILENCE_THRESH = -40  # dB
    MIN_SILENCE_LEN = 500  # ms
    
    def __init__(self, output_dir: str = "transcriptions"):
        """
        Initialize the transcription service.
        
        Args:
            output_dir: Directory to store transcription results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.recognizer = sr.Recognizer()
        
        # Performance tuning
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
    
    def get_file_hash(self, file_path: str) -> str:
        """Generate a unique hash for the audio file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def validate_audio_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate audio file format and size.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            return False, f"File not found: {file_path}"
        
        # Check file extension
        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return False, f"Unsupported format: {file_path.suffix}. Supported: {self.SUPPORTED_FORMATS}"
        
        # Check file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            return False, f"File too large: {file_size_mb:.2f}MB (max: {self.MAX_FILE_SIZE_MB}MB)"
        
        return True, None
    
    def convert_to_wav(self, audio_path: str) -> str:
        """
        Convert audio file to WAV format for processing.
        Handles different audio formats transparently.
        
        Args:
            audio_path: Path to the input audio file
            
        Returns:
            Path to the converted WAV file
        """
        audio_path = Path(audio_path)
        
        # If already WAV, return as-is
        if audio_path.suffix.lower() == '.wav':
            logger.info(f"File already in WAV format: {audio_path}")
            return str(audio_path)
        
        logger.info(f"Converting {audio_path.suffix} to WAV format")
        
        try:
            # Load audio file (pydub handles format detection)
            audio = AudioSegment.from_file(str(audio_path))
            
            # Convert to WAV with standard settings
            wav_path = audio_path.with_suffix('.wav')
            audio.export(
                str(wav_path),
                format='wav',
                parameters=["-ac", "1", "-ar", "16000"]  # Mono, 16kHz
            )
            
            logger.info(f"Converted to: {wav_path}")
            return str(wav_path)
            
        except Exception as e:
            logger.error(f"Error converting audio format: {str(e)}")
            raise
    
    def chunk_audio_by_time(self, audio_path: str) -> List[AudioSegment]:
        """
        Split long audio files into fixed-length chunks.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            List of audio chunks
        """
        logger.info(f"Loading audio file: {audio_path}")
        audio = AudioSegment.from_wav(audio_path)
        
        duration_ms = len(audio)
        logger.info(f"Audio duration: {duration_ms/1000:.2f} seconds")
        
        chunks = []
        for start_ms in range(0, duration_ms, self.CHUNK_LENGTH_MS):
            end_ms = min(start_ms + self.CHUNK_LENGTH_MS, duration_ms)
            chunk = audio[start_ms:end_ms]
            chunks.append(chunk)
        
        logger.info(f"Split into {len(chunks)} chunks")
        return chunks
    
    def chunk_audio_by_silence(self, audio_path: str) -> List[AudioSegment]:
        """
        Split audio on silence for more natural segmentation.
        Fallback to time-based chunking if silence detection fails.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            List of audio chunks
        """
        logger.info(f"Attempting silence-based chunking: {audio_path}")
        
        try:
            audio = AudioSegment.from_wav(audio_path)
            
            chunks = split_on_silence(
                audio,
                min_silence_len=self.MIN_SILENCE_LEN,
                silence_thresh=self.SILENCE_THRESH,
                keep_silence=200  # Keep 200ms of silence at edges
            )
            
            # If chunks are too large, fall back to time-based chunking
            max_chunk_len = max(len(chunk) for chunk in chunks) if chunks else 0
            
            if not chunks or max_chunk_len > self.CHUNK_LENGTH_MS * 2:
                logger.warning("Silence detection produced suboptimal chunks, using time-based chunking")
                return self.chunk_audio_by_time(audio_path)
            
            logger.info(f"Silence-based chunking created {len(chunks)} segments")
            return chunks
            
        except Exception as e:
            logger.warning(f"Silence detection failed: {str(e)}, falling back to time-based chunking")
            return self.chunk_audio_by_time(audio_path)
    
    def transcribe_chunk(self, audio_chunk: AudioSegment, chunk_index: int) -> Optional[str]:
        """
        Transcribe a single audio chunk using Google Speech Recognition.
        
        Args:
            audio_chunk: Audio segment to transcribe
            chunk_index: Index of the chunk for logging
            
        Returns:
            Transcribed text or None if transcription fails
        """
        try:
            # Export chunk to temporary WAV file
            temp_path = f"/tmp/chunk_{chunk_index}.wav"
            audio_chunk.export(temp_path, format="wav")
            
            # Load audio data
            with sr.AudioFile(temp_path) as source:
                audio_data = self.recognizer.record(source)
            
            # Perform transcription
            text = self.recognizer.recognize_google(audio_data)
            
            # Cleanup
            os.remove(temp_path)
            
            logger.info(f"Chunk {chunk_index} transcribed successfully")
            return text
            
        except sr.UnknownValueError:
            logger.warning(f"Chunk {chunk_index}: Speech not understood")
            return None
        except sr.RequestError as e:
            logger.error(f"Chunk {chunk_index}: API error - {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Chunk {chunk_index}: Unexpected error - {str(e)}")
            return None
    
    def transcribe(
        self, 
        audio_path: str, 
        use_silence_detection: bool = True
    ) -> Dict:
        """
        Main transcription method with timestamps per segment.
        
        Args:
            audio_path: Path to the audio file
            use_silence_detection: Whether to use silence-based chunking
            
        Returns:
            Dictionary containing transcription results with timestamps
        """
        start_time = datetime.now()
        
        # Validate file
        is_valid, error_msg = self.validate_audio_file(audio_path)
        if not is_valid:
            return {
                'status': 'error',
                'error': error_msg,
                'timestamp': start_time.isoformat()
            }
        
        try:
            # Convert to WAV if needed
            wav_path = self.convert_to_wav(audio_path)
            
            # Generate file hash for deduplication
            file_hash = self.get_file_hash(wav_path)
            
            # Chunk the audio
            if use_silence_detection:
                chunks = self.chunk_audio_by_silence(wav_path)
            else:
                chunks = self.chunk_audio_by_time(wav_path)
            
            # Transcribe each chunk
            segments = []
            current_time_ms = 0
            
            for i, chunk in enumerate(chunks):
                chunk_duration_ms = len(chunk)
                
                # Transcribe
                text = self.transcribe_chunk(chunk, i)
                
                if text:
                    segment = {
                        'segment_id': i,
                        'start_time': current_time_ms / 1000.0,  # Convert to seconds
                        'end_time': (current_time_ms + chunk_duration_ms) / 1000.0,
                        'duration': chunk_duration_ms / 1000.0,
                        'text': text,
                        'confidence': 'high'  # Google API doesn't provide confidence scores
                    }
                    segments.append(segment)
                
                current_time_ms += chunk_duration_ms
            
            # Compile full transcript
            full_transcript = " ".join(seg['text'] for seg in segments)
            
            # Calculate total duration
            total_duration = current_time_ms / 1000.0
            
            # Build result
            result = {
                'status': 'success',
                'file_hash': file_hash,
                'file_name': Path(audio_path).name,
                'file_size_mb': Path(audio_path).stat().st_size / (1024 * 1024),
                'total_duration': total_duration,
                'num_segments': len(segments),
                'transcript': full_transcript,
                'segments': segments,
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'timestamp': start_time.isoformat()
            }
            
            # Save result
            self._save_result(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': start_time.isoformat()
            }
    
    def _save_result(self, result: Dict) -> None:
        """Save transcription result to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"transcript_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"Result saved to: {output_file}")


def main():
    """Example usage of the transcription service."""
    service = TranscriptionService()
    
    # Example: Transcribe an audio file
    audio_file = "sample_audio.wav"
    
    if os.path.exists(audio_file):
        result = service.transcribe(audio_file)
        print(json.dumps(result, indent=2))
    else:
        print(f"Sample audio file not found: {audio_file}")
        print("Please provide an audio file to test the service.")


if __name__ == "__main__":
    main()
