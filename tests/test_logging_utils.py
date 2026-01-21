"""Unit tests for logging utilities."""
import unittest
import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch, mock_open
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bin.utils import logging_utils


class TestLoggingUtils(unittest.TestCase):
    """Test logging utility functions."""

    def setUp(self):
        """Reset log file before each test."""
        logging_utils.CURRENT_LOG_FILE = None

    def test_set_log_file(self):
        """Test setting the log file path."""
        test_path = Path("/tmp/test.log")
        logging_utils.set_log_file(test_path)
        self.assertEqual(logging_utils.CURRENT_LOG_FILE, test_path)

    @patch('sys.stdout', new_callable=StringIO)
    def test_log_prints_to_stdout(self, mock_stdout):
        """Test that log messages are printed to stdout."""
        test_message = "Test log message"
        logging_utils.log(test_message)
        output = mock_stdout.getvalue()
        self.assertIn(test_message, output)
        self.assertIn("[PIPELINE]", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_log_includes_timestamp(self, mock_stdout):
        """Test that log messages include timestamps."""
        logging_utils.log("Test")
        output = mock_stdout.getvalue()
        # Check for timestamp format (YYYY-MM-DD HH:MM:SS)
        # Look for the pattern [PIPELINE] YYYY-MM-DD HH:MM:SS -
        import re
        timestamp_pattern = r'\[PIPELINE\] \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} -'
        self.assertRegex(output, timestamp_pattern, "Log should include timestamp in format YYYY-MM-DD HH:MM:SS")

    @patch('sys.stdout', new_callable=StringIO)
    @patch('pathlib.Path.open', new_callable=mock_open)
    def test_log_writes_to_file_when_set(self, mock_file, mock_stdout):
        """Test that log messages are written to file when log file is set."""
        test_path = Path("/tmp/test.log")
        logging_utils.set_log_file(test_path)
        test_message = "Test log message"
        
        logging_utils.log(test_message)
        
        # Verify file was opened and written to
        mock_file.assert_called()
        handle = mock_file()
        handle.write.assert_called()
        
        # Check that the test message was part of what was written
        written_content = ''.join([call.args[0] if call.args else '' for call in handle.write.call_args_list])
        self.assertIn(test_message, written_content)


if __name__ == '__main__':
    unittest.main()
