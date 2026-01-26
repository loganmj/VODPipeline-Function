"""Client for posting job status events to the API."""
import json
import urllib.request
import urllib.error
from typing import Optional
import time

from bin.models.job_status import JobStatus
from bin.utils.logging_utils import log


class JobStatusClient:
    """
    Client for posting JobStatus events to the API.
    
    This client handles communication with the API endpoint for job status updates.
    It includes retry logic for transient failures and never blocks the pipeline
    if the API is unavailable.
    """
    
    def __init__(self, api_base_url: Optional[str] = None, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize the JobStatusClient.
        
        Args:
            api_base_url: Base URL of the API (e.g., "http://localhost:5000")
            max_retries: Maximum number of retry attempts for failed requests
            retry_delay: Delay in seconds between retry attempts
        """
        self.api_base_url = api_base_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.enabled = api_base_url is not None and len(api_base_url.strip()) > 0
    
    def post_status(self, job_status: JobStatus) -> bool:
        """
        Post a JobStatus event to the API.
        
        This method will retry on transient failures and will never block the pipeline
        if the API is unavailable. All errors are logged but do not raise exceptions.
        
        Args:
            job_status: The JobStatus event to post
            
        Returns:
            bool: True if the event was successfully posted, False otherwise
        """
        if not self.enabled:
            log(f"[JOB_STATUS] API communication disabled, skipping event: {job_status.stage}")
            return False
        
        endpoint = f"{self.api_base_url}/api/events/job"
        data = json.dumps(job_status.to_dict()).encode('utf-8')
        
        for attempt in range(1, self.max_retries + 1):
            try:
                req = urllib.request.Request(
                    endpoint,
                    data=data,
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                
                with urllib.request.urlopen(req, timeout=5) as response:
                    if response.status in (200, 201, 202):
                        log(f"[JOB_STATUS] Successfully posted {job_status.stage} event (attempt {attempt})")
                        return True
                    else:
                        log(f"[JOB_STATUS] Unexpected status code {response.status} for {job_status.stage} event")
                        
            except urllib.error.HTTPError as e:
                log(f"[JOB_STATUS] HTTP error posting {job_status.stage} event (attempt {attempt}): {e.code} {e.reason}")
            except urllib.error.URLError as e:
                log(f"[JOB_STATUS] URL error posting {job_status.stage} event (attempt {attempt}): {e.reason}")
            except Exception as e:
                log(f"[JOB_STATUS] Unexpected error posting {job_status.stage} event (attempt {attempt}): {e}")
            
            # Wait before retrying (except on last attempt)
            if attempt < self.max_retries:
                time.sleep(self.retry_delay)
        
        log(f"[JOB_STATUS] Failed to post {job_status.stage} event after {self.max_retries} attempts")
        return False
    
    def post_started(self, job_id: str, file_name: str) -> bool:
        """Post a jobStarted event."""
        status = JobStatus.create_started(job_id, file_name)
        return self.post_status(status)
    
    def post_progress(self, job_id: str, file_name: str, stage: str, percent: int) -> bool:
        """Post a jobProgressUpdated event."""
        status = JobStatus.create_progress(job_id, file_name, stage, percent)
        return self.post_status(status)
    
    def post_stage_changed(self, job_id: str, file_name: str, stage: str, percent: int) -> bool:
        """Post a jobStageChanged event."""
        status = JobStatus.create_stage_changed(job_id, file_name, stage, percent)
        return self.post_status(status)
    
    def post_completed(self, job_id: str, file_name: str) -> bool:
        """Post a jobCompleted event."""
        status = JobStatus.create_completed(job_id, file_name)
        return self.post_status(status)
    
    def post_failed(self, job_id: str, file_name: str, error_message: str, current_percent: int = 0) -> bool:
        """Post a jobFailed event."""
        status = JobStatus.create_failed(job_id, file_name, error_message, current_percent)
        return self.post_status(status)
