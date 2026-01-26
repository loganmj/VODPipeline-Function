#!/usr/bin/env python3
"""
Demonstration of the unified emit_event() API for job status events.

This example shows how to use the emit_event() method to emit events
throughout the processing lifecycle of a video file.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bin.clients.job_status_client import JobStatusClient


def main():
    """Demonstrate the event emission API."""
    print("=== Event Emission Pipeline Demo ===\n")
    
    # Initialize the client
    # In production, API_BASE_URL would be set via environment variable
    # For this demo, we'll use None to run without API communication
    client = JobStatusClient(api_base_url=None)
    
    # Example job details
    job_id = "demo-job-123"
    file_name = "example-video.mp4"
    
    print("1. Job Started")
    print(f"   emit_event('{job_id}', '{file_name}', 'Starting', 0)")
    client.emit_event(job_id, file_name, "Starting", 0)
    print("   ✓ Internal state updated: stage='Starting', percent=0, is_running=True\n")
    
    print("2. Stage Changed: Silence Removal")
    print(f"   emit_event('{job_id}', '{file_name}', 'Silence Removal', 10)")
    client.emit_event(job_id, file_name, "Silence Removal", 10)
    print("   ✓ Internal state updated: stage='Silence Removal', percent=10\n")
    
    print("3. Progress Update (within Silence Removal stage)")
    print(f"   emit_event('{job_id}', '{file_name}', 'Silence Removal', 40)")
    client.emit_event(job_id, file_name, "Silence Removal", 40)
    print("   ✓ Internal state updated: percent=40\n")
    
    print("4. Stage Changed: Scene Detection")
    print(f"   emit_event('{job_id}', '{file_name}', 'Scene Detection', 50)")
    client.emit_event(job_id, file_name, "Scene Detection", 50)
    print("   ✓ Internal state updated: stage='Scene Detection', percent=50\n")
    
    print("5. Progress Update (within Scene Detection stage)")
    print(f"   emit_event('{job_id}', '{file_name}', 'Scene Detection', 70)")
    client.emit_event(job_id, file_name, "Scene Detection", 70)
    print("   ✓ Internal state updated: percent=70\n")
    
    print("6. Stage Changed: Highlight Extraction")
    print(f"   emit_event('{job_id}', '{file_name}', 'Highlight Extraction', 75)")
    client.emit_event(job_id, file_name, "Highlight Extraction", 75)
    print("   ✓ Internal state updated: stage='Highlight Extraction', percent=75\n")
    
    print("7. Progress Update (within Highlight Extraction stage)")
    print(f"   emit_event('{job_id}', '{file_name}', 'Highlight Extraction', 90)")
    client.emit_event(job_id, file_name, "Highlight Extraction", 90)
    print("   ✓ Internal state updated: percent=90\n")
    
    print("8. Stage Changed: Archiving")
    print(f"   emit_event('{job_id}', '{file_name}', 'Archiving', 95)")
    client.emit_event(job_id, file_name, "Archiving", 95)
    print("   ✓ Internal state updated: stage='Archiving', percent=95\n")
    
    print("9. Job Completed")
    print(f"   emit_event('{job_id}', '{file_name}', 'Completed', 100)")
    client.emit_event(job_id, file_name, "Completed", 100)
    print("   ✓ Internal state updated: stage='Completed', percent=100, is_running=False\n")
    
    print("=== Demo Complete ===\n")
    
    # Show how to handle errors
    print("\n=== Error Handling Demo ===\n")
    
    job_id_2 = "demo-job-456"
    file_name_2 = "another-video.mp4"
    
    print("1. Job Started")
    print(f"   emit_event('{job_id_2}', '{file_name_2}', 'Starting', 0)")
    client.emit_event(job_id_2, file_name_2, "Starting", 0)
    print("   ✓ Internal state updated\n")
    
    print("2. Stage Changed: Silence Removal")
    print(f"   emit_event('{job_id_2}', '{file_name_2}', 'Silence Removal', 10)")
    client.emit_event(job_id_2, file_name_2, "Silence Removal", 10)
    print("   ✓ Internal state updated\n")
    
    print("3. Error Occurred - Job Failed")
    print(f"   emit_event('{job_id_2}', '{file_name_2}', 'Failed', 10, error_message='FFmpeg processing error')")
    client.emit_event(job_id_2, file_name_2, "Failed", 10, error_message="FFmpeg processing error")
    print("   ✓ Internal state updated: stage='Failed', error_message='FFmpeg processing error', is_running=False\n")
    
    print("=== Error Handling Demo Complete ===\n")
    
    # Show the final state
    print("\n=== Current State ===")
    state = client.state_manager.get_state()
    print(f"Job ID: {state.job_id}")
    print(f"File Name: {state.file_name}")
    print(f"Stage: {state.stage}")
    print(f"Percent: {state.percent}%")
    print(f"Is Running: {state.is_running}")
    print(f"Error Message: {state.error_message}")
    print(f"Last Updated: {state.last_updated_at}")


if __name__ == "__main__":
    main()
