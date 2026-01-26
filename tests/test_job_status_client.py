"""Unit tests for JobStatusClient."""
import json
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

    @patch('urllib.request.urlopen')
    @patch('urllib.request.Request')
    def test_emit_event_starting(self, mock_request, mock_urlopen):
        """Test emit_event for jobStarted event."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        client = JobStatusClient(api_base_url="http://localhost:5000")
        result = client.emit_event("test-id", "test.mp4", "Starting", 0)
        
        self.assertTrue(result)
        self.assertEqual(mock_urlopen.call_count, 1)
        
        # Verify the request payload
        call_args = mock_request.call_args
        posted_data = json.loads(call_args[1]['data'].decode('utf-8'))
        self.assertEqual(posted_data['stage'], "Starting")
        self.assertEqual(posted_data['percent'], 0)
        self.assertEqual(posted_data['jobId'], "test-id")
        self.assertEqual(posted_data['fileName'], "test.mp4")
        self.assertIsNone(posted_data['errorMessage'])
        
        # Verify internal state was updated
        state = client.state_manager.get_state()
        self.assertEqual(state.stage, "Starting")
        self.assertEqual(state.percent, 0)
        self.assertEqual(state.job_id, "test-id")
        self.assertEqual(state.file_name, "test.mp4")
        self.assertTrue(state.is_running)
    
    @patch('urllib.request.urlopen')
    @patch('urllib.request.Request')
    def test_emit_event_stage_change(self, mock_request, mock_urlopen):
        """Test emit_event for stage change."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        client = JobStatusClient(api_base_url="http://localhost:5000")
        # First, start a job
        client.emit_event("test-id", "test.mp4", "Starting", 0)
        # Then change stage
        result = client.emit_event("test-id", "test.mp4", "Processing", 20)
        
        self.assertTrue(result)
        # Should have called urlopen twice (once for starting, once for stage change)
        self.assertEqual(mock_urlopen.call_count, 2)
        
        # Verify the second call was a stage change with correct payload
        second_call_args = mock_request.call_args_list[1]
        posted_data = json.loads(second_call_args[1]['data'].decode('utf-8'))
        self.assertEqual(posted_data['stage'], "Processing")
        self.assertEqual(posted_data['percent'], 20)
        self.assertEqual(posted_data['jobId'], "test-id")
        self.assertEqual(posted_data['fileName'], "test.mp4")
        
        # Verify internal state reflects the stage change
        state = client.state_manager.get_state()
        self.assertEqual(state.stage, "Processing")
        self.assertEqual(state.percent, 20)
        self.assertTrue(state.is_running)
    
    @patch('urllib.request.urlopen')
    @patch('urllib.request.Request')
    def test_emit_event_progress_update(self, mock_request, mock_urlopen):
        """Test emit_event for progress update within same stage."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        client = JobStatusClient(api_base_url="http://localhost:5000")
        # Start job and set stage
        client.emit_event("test-id", "test.mp4", "Starting", 0)
        client.emit_event("test-id", "test.mp4", "Processing", 20)
        # Update progress in same stage
        result = client.emit_event("test-id", "test.mp4", "Processing", 50)
        
        self.assertTrue(result)
        # Should have called urlopen three times
        self.assertEqual(mock_urlopen.call_count, 3)
        
        # Verify the third call was a progress update (same stage, different percent)
        third_call_args = mock_request.call_args_list[2]
        posted_data = json.loads(third_call_args[1]['data'].decode('utf-8'))
        self.assertEqual(posted_data['stage'], "Processing")
        self.assertEqual(posted_data['percent'], 50)
        self.assertEqual(posted_data['jobId'], "test-id")
        self.assertEqual(posted_data['fileName'], "test.mp4")
        
        # Verify internal state reflects the progress update
        state = client.state_manager.get_state()
        self.assertEqual(state.stage, "Processing")
        self.assertEqual(state.percent, 50)
        self.assertTrue(state.is_running)
    
    @patch('urllib.request.urlopen')
    @patch('urllib.request.Request')
    def test_emit_event_completed(self, mock_request, mock_urlopen):
        """Test emit_event for jobCompleted event."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        client = JobStatusClient(api_base_url="http://localhost:5000")
        result = client.emit_event("test-id", "test.mp4", "Completed", 100)
        
        self.assertTrue(result)
        self.assertEqual(mock_urlopen.call_count, 1)
        
        # Verify the request payload
        call_args = mock_request.call_args
        posted_data = json.loads(call_args[1]['data'].decode('utf-8'))
        self.assertEqual(posted_data['stage'], "Completed")
        self.assertEqual(posted_data['percent'], 100)
        self.assertEqual(posted_data['jobId'], "test-id")
        self.assertEqual(posted_data['fileName'], "test.mp4")
        
        # Verify internal state was updated
        state = client.state_manager.get_state()
        self.assertEqual(state.stage, "Completed")
        self.assertEqual(state.percent, 100)
        self.assertFalse(state.is_running)
    
    @patch('urllib.request.urlopen')
    @patch('urllib.request.Request')
    def test_emit_event_failed(self, mock_request, mock_urlopen):
        """Test emit_event for jobFailed event."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        client = JobStatusClient(api_base_url="http://localhost:5000")
        result = client.emit_event("test-id", "test.mp4", "Failed", 35, error_message="Test error")
        
        self.assertTrue(result)
        self.assertEqual(mock_urlopen.call_count, 1)
        
        # Verify the request payload includes error message and correct percent
        call_args = mock_request.call_args
        posted_data = json.loads(call_args[1]['data'].decode('utf-8'))
        self.assertEqual(posted_data['stage'], "Failed")
        self.assertEqual(posted_data['percent'], 35)
        self.assertEqual(posted_data['jobId'], "test-id")
        self.assertEqual(posted_data['fileName'], "test.mp4")
        self.assertEqual(posted_data['errorMessage'], "Test error")
        
        # Verify internal state was updated (note: percent is not updated in state for failures)
        state = client.state_manager.get_state()
        self.assertEqual(state.stage, "Failed")
        self.assertEqual(state.error_message, "Test error")
        self.assertFalse(state.is_running)
    
    @patch('urllib.request.urlopen')
    @patch('urllib.request.Request')
    def test_emit_event_failed_default_error_message(self, mock_request, mock_urlopen):
        """Test emit_event for jobFailed event with no error message."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        client = JobStatusClient(api_base_url="http://localhost:5000")
        result = client.emit_event("test-id", "test.mp4", "Failed", 35)
        
        self.assertTrue(result)
        self.assertEqual(mock_urlopen.call_count, 1)
        
        # Verify the request payload includes default error message and correct percent
        call_args = mock_request.call_args
        posted_data = json.loads(call_args[1]['data'].decode('utf-8'))
        self.assertEqual(posted_data['stage'], "Failed")
        self.assertEqual(posted_data['percent'], 35)
        self.assertEqual(posted_data['errorMessage'], "Unknown error")
        
        # Verify internal state was updated with default error message
        state = client.state_manager.get_state()
        self.assertEqual(state.stage, "Failed")
        self.assertEqual(state.error_message, "Unknown error")
        self.assertFalse(state.is_running)


if __name__ == '__main__':
    unittest.main()
