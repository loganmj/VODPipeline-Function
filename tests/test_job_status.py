"""Unit tests for JobStatus DTO."""
import unittest
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bin.models.job_status import JobStatus


class TestJobStatus(unittest.TestCase):
    """Test JobStatus DTO functionality."""

    def test_job_status_creation(self):
        """Test basic JobStatus creation."""
        job_status = JobStatus(
            job_id="test-job-id",
            file_name="test-video.mp4",
            stage="Processing",
            percent=50,
            timestamp=datetime.now(timezone.utc)
        )
        
        self.assertEqual(job_status.job_id, "test-job-id")
        self.assertEqual(job_status.file_name, "test-video.mp4")
        self.assertEqual(job_status.stage, "Processing")
        self.assertEqual(job_status.percent, 50)
        self.assertIsInstance(job_status.timestamp, datetime)
        self.assertIsNone(job_status.error_message)

    def test_job_status_with_error(self):
        """Test JobStatus creation with error message."""
        job_status = JobStatus(
            job_id="test-job-id",
            file_name="test-video.mp4",
            stage="Failed",
            percent=30,
            timestamp=datetime.now(timezone.utc),
            error_message="Test error message"
        )
        
        self.assertEqual(job_status.error_message, "Test error message")

    def test_to_dict(self):
        """Test JobStatus to_dict serialization."""
        timestamp = datetime.now(timezone.utc)
        job_status = JobStatus(
            job_id="test-job-id",
            file_name="test-video.mp4",
            stage="Processing",
            percent=50,
            timestamp=timestamp
        )
        
        result = job_status.to_dict()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["jobId"], "test-job-id")
        self.assertEqual(result["fileName"], "test-video.mp4")
        self.assertEqual(result["stage"], "Processing")
        self.assertEqual(result["percent"], 50)
        self.assertEqual(result["timestamp"], timestamp.isoformat())
        self.assertIsNone(result["errorMessage"])

    def test_create_started(self):
        """Test factory method for jobStarted event."""
        job_status = JobStatus.create_started("test-job-id", "test-video.mp4")
        
        self.assertEqual(job_status.job_id, "test-job-id")
        self.assertEqual(job_status.file_name, "test-video.mp4")
        self.assertEqual(job_status.stage, "Starting")
        self.assertEqual(job_status.percent, 0)
        self.assertIsInstance(job_status.timestamp, datetime)
        self.assertIsNone(job_status.error_message)

    def test_create_progress(self):
        """Test factory method for jobProgressUpdated event."""
        job_status = JobStatus.create_progress("test-job-id", "test-video.mp4", "Silence Removal", 42)
        
        self.assertEqual(job_status.job_id, "test-job-id")
        self.assertEqual(job_status.file_name, "test-video.mp4")
        self.assertEqual(job_status.stage, "Silence Removal")
        self.assertEqual(job_status.percent, 42)
        self.assertIsInstance(job_status.timestamp, datetime)
        self.assertIsNone(job_status.error_message)

    def test_create_stage_changed(self):
        """Test factory method for jobStageChanged event."""
        job_status = JobStatus.create_stage_changed("test-job-id", "test-video.mp4", "Encoding", 60)
        
        self.assertEqual(job_status.job_id, "test-job-id")
        self.assertEqual(job_status.file_name, "test-video.mp4")
        self.assertEqual(job_status.stage, "Encoding")
        self.assertEqual(job_status.percent, 60)
        self.assertIsInstance(job_status.timestamp, datetime)
        self.assertIsNone(job_status.error_message)

    def test_create_completed(self):
        """Test factory method for jobCompleted event."""
        job_status = JobStatus.create_completed("test-job-id", "test-video.mp4")
        
        self.assertEqual(job_status.job_id, "test-job-id")
        self.assertEqual(job_status.file_name, "test-video.mp4")
        self.assertEqual(job_status.stage, "Completed")
        self.assertEqual(job_status.percent, 100)
        self.assertIsInstance(job_status.timestamp, datetime)
        self.assertIsNone(job_status.error_message)

    def test_create_failed(self):
        """Test factory method for jobFailed event."""
        job_status = JobStatus.create_failed("test-job-id", "test-video.mp4", "Test error", 35)
        
        self.assertEqual(job_status.job_id, "test-job-id")
        self.assertEqual(job_status.file_name, "test-video.mp4")
        self.assertEqual(job_status.stage, "Failed")
        self.assertEqual(job_status.percent, 35)
        self.assertIsInstance(job_status.timestamp, datetime)
        self.assertEqual(job_status.error_message, "Test error")


if __name__ == '__main__':
    unittest.main()
