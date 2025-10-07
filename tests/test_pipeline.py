"""Tests for the pipeline module."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from call2action.pipeline import TranscriptPipeline
from call2action.config import Settings
from call2action.models import TranscriptSegment, TranscriptResult


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    return Settings(
        openai_api_key="test-key",
        openai_model="gpt-4o-mini",
        whisper_model_size="base",
        whisper_device="cpu",
        whisper_compute_type="int8",
    )


@pytest.fixture
def mock_transcript_data():
    """Create mock transcript data."""
    segments = [
        TranscriptSegment(start=0.0, end=5.0, text="Hello, welcome to the meeting."),
        TranscriptSegment(start=5.0, end=10.0, text="Let's discuss the project timeline."),
    ]
    transcript = " ".join([seg.text for seg in segments])
    return transcript, segments


def test_pipeline_initialization(mock_settings):
    """Test that the pipeline initializes correctly."""
    with patch('call2action.pipeline.Transcriber'), \
         patch('call2action.pipeline.Summarizer'):
        pipeline = TranscriptPipeline(settings=mock_settings)
        assert pipeline.settings == mock_settings
        assert pipeline.transcriber is not None
        assert pipeline.summarizer is not None


def test_pipeline_process(mock_settings, mock_transcript_data):
    """Test the complete pipeline process."""
    transcript, segments = mock_transcript_data
    
    with patch('call2action.pipeline.Transcriber') as MockTranscriber, \
         patch('call2action.pipeline.Summarizer') as MockSummarizer:
        
        # Setup mocks
        mock_transcriber = Mock()
        mock_transcriber.transcribe.return_value = (transcript, segments)
        MockTranscriber.return_value = mock_transcriber
        
        mock_summarizer = Mock()
        mock_summarizer.generate_summary.return_value = "Test summary"
        mock_summarizer.generate_call_to_action.return_value = ["Action 1", "Action 2"]
        MockSummarizer.return_value = mock_summarizer
        
        # Run pipeline
        pipeline = TranscriptPipeline(settings=mock_settings)
        result = pipeline.process("test_audio.mp4", save_output=False)
        
        # Assertions
        assert isinstance(result, TranscriptResult)
        assert result.transcript == transcript
        assert result.summary == "Test summary"
        assert len(result.call_to_action) == 2
        assert result.segments == segments
