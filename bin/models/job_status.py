"""JobStatus DTO for communicating job progress to the API."""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import uuid


@dataclass
class JobStatus:
    """
    Data Transfer Object for job status information.
    
    This DTO is used to communicate job progress from the Function to the API.
    It contains all information needed to track job lifecycle events.
    """
    job_id: str
    file_name: str
    stage: str
    percent: int
    timestamp: datetime
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """
        Convert JobStatus to a dictionary suitable for JSON serialization.
        
        Returns:
            dict: Dictionary representation with ISO format timestamp
        """
        return {
            "jobId": self.job_id,
            "fileName": self.file_name,
            "stage": self.stage,
            "percent": self.percent,
            "timestamp": self.timestamp.isoformat(),
            "errorMessage": self.error_message
        }
    
    @staticmethod
    def create_started(job_id: str, file_name: str) -> "JobStatus":
        """Create a jobStarted event."""
        return JobStatus(
            job_id=job_id,
            file_name=file_name,
            stage="Starting",
            percent=0,
            timestamp=datetime.now(timezone.utc)
        )
    
    @staticmethod
    def create_progress(job_id: str, file_name: str, stage: str, percent: int) -> "JobStatus":
        """Create a jobProgressUpdated event."""
        return JobStatus(
            job_id=job_id,
            file_name=file_name,
            stage=stage,
            percent=percent,
            timestamp=datetime.now(timezone.utc)
        )
    
    @staticmethod
    def create_stage_changed(job_id: str, file_name: str, stage: str, percent: int) -> "JobStatus":
        """Create a jobStageChanged event."""
        return JobStatus(
            job_id=job_id,
            file_name=file_name,
            stage=stage,
            percent=percent,
            timestamp=datetime.now(timezone.utc)
        )
    
    @staticmethod
    def create_completed(job_id: str, file_name: str) -> "JobStatus":
        """Create a jobCompleted event."""
        return JobStatus(
            job_id=job_id,
            file_name=file_name,
            stage="Completed",
            percent=100,
            timestamp=datetime.now(timezone.utc)
        )
    
    @staticmethod
    def create_failed(job_id: str, file_name: str, error_message: str, current_percent: int = 0) -> "JobStatus":
        """Create a jobFailed event."""
        return JobStatus(
            job_id=job_id,
            file_name=file_name,
            stage="Failed",
            percent=current_percent,
            timestamp=datetime.now(timezone.utc),
            error_message=error_message
        )
