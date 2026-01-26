"""Unit tests for JobStatusClient."""
import unittest
import sys
from pathlib import Path
from unittest.mock import patch, Mock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bin.clients.job_status_client import JobStatusClient
from bin.models.job_status import JobStatus


class TestJobStatusClient(unittest.TestCase):
    """Test JobStatusClient functionality."""

    def test_client_disabled_when_no_url(self):
        """Test that client is disabled when API URL is not provided."""
        client = JobStatusClient(api_base_url=None)
        self.assertFalse(client.enabled)
        
        client = JobStatusClient(api_base_url="")
        self.assertFalse(client.enabled)
        
        client = JobStatusClient(api_base_url="   ")
        self.assertFalse(client.enabled)

    def test_client_enabled_with_url(self):
        """Test that client is enabled when API URL is provided."""
        client = JobStatusClient(api_base_url="http://localhost:5000")
        self.assertTrue(client.enabled)

    def test_post_status_disabled(self):
        """Test that post_status returns False when client is disabled."""
        client = JobStatusClient(api_base_url=None)
        job_status = JobStatus.create_started("test-id", "test.mp4")
        
        result = client.post_status(job_status)
        self.assertFalse(result)

    @patch('urllib.request.urlopen')
    def test_post_status_success(self, mock_urlopen):
        """Test successful status post."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        client = JobStatusClient(api_base_url="http://localhost:5000")
        job_status = JobStatus.create_started("test-id", "test.mp4")
        
        result = client.post_status(job_status)
        self.assertTrue(result)

    @patch('urllib.request.urlopen')
    def test_post_status_retry_on_failure(self, mock_urlopen):
        """Test retry logic on failure."""
        # Mock failure response
        mock_urlopen.side_effect = Exception("Connection error")
        
        client = JobStatusClient(api_base_url="http://localhost:5000", max_retries=2, retry_delay=0.1)
        job_status = JobStatus.create_started("test-id", "test.mp4")
        
        result = client.post_status(job_status)
        self.assertFalse(result)
        # Should have tried max_retries times
        self.assertEqual(mock_urlopen.call_count, 2)

    @patch('urllib.request.urlopen')
    def test_post_started_convenience_method(self, mock_urlopen):
        """Test post_started convenience method."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        client = JobStatusClient(api_base_url="http://localhost:5000")
        result = client.post_started("test-id", "test.mp4")
        
        self.assertTrue(result)
        self.assertEqual(mock_urlopen.call_count, 1)

    @patch('urllib.request.urlopen')
    def test_post_progress_convenience_method(self, mock_urlopen):
        """Test post_progress convenience method."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        client = JobStatusClient(api_base_url="http://localhost:5000")
        result = client.post_progress("test-id", "test.mp4", "Processing", 50)
        
        self.assertTrue(result)
        self.assertEqual(mock_urlopen.call_count, 1)

    @patch('urllib.request.urlopen')
    def test_post_completed_convenience_method(self, mock_urlopen):
        """Test post_completed convenience method."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        client = JobStatusClient(api_base_url="http://localhost:5000")
        result = client.post_completed("test-id", "test.mp4")
        
        self.assertTrue(result)
        self.assertEqual(mock_urlopen.call_count, 1)

    @patch('urllib.request.urlopen')
    def test_post_failed_convenience_method(self, mock_urlopen):
        """Test post_failed convenience method."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        client = JobStatusClient(api_base_url="http://localhost:5000")
        result = client.post_failed("test-id", "test.mp4", "Error message", 30)
        
        self.assertTrue(result)
        self.assertEqual(mock_urlopen.call_count, 1)


if __name__ == '__main__':
    unittest.main()
