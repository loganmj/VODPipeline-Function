import time
import shutil
from pathlib import Path
import psutil
import threading
import uuid

from bin.config import (
    INPUT_DIR,
    EXPORT_BASE,
    TMP_DIR,
    ARCHIVE_DIR,
    SILENCE_NOISE_DB,
    SILENCE_MIN_DURATION,
    API_BASE_URL,
)

from bin.utils.logging_utils import log, set_log_file
from bin.utils.silence_remove import remove_silence, get_duration
from bin.utils.scene_detect import run_scene_detect, parse_scenes_csv
from bin.utils.highlights import extract_highlights
from bin.clients.job_status_client import JobStatusClient


def start_resource_monitor():
    samples = {"cpu": [], "ram": []}
    control = {"running": True}

    def monitor():
        proc = psutil.Process()
        while control["running"]:
            samples["cpu"].append(proc.cpu_percent(interval=0.5))
            samples["ram"].append(proc.memory_info().rss / (1024 * 1024))
            time.sleep(0.5)

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()

    def stop():
        control["running"] = False

    return samples, stop


def run_for_file(input_path: Path):
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    file_name = input_path.name
    
    # Initialize job status client
    status_client = JobStatusClient(api_base_url=API_BASE_URL)
    
    # Track current progress for failure reporting
    current_percent = 0
    
    # Ensure the output base directory exists
    EXPORT_BASE.mkdir(parents=True, exist_ok=True)

    job_dir = EXPORT_BASE / input_path.stem
    job_dir.mkdir(parents=True, exist_ok=True)

    # Per-file log
    log_path = job_dir / "pipeline.log"
    set_log_file(log_path)

    log(f"[PIPELINE] Starting pipeline for {input_path} (Job ID: {job_id})")
    
    # Emit jobStarted event
    status_client.post_started(job_id, file_name)

    # Resource monitoring
    start_time = time.time()
    samples, stop_monitor = start_resource_monitor()

    try:
        # Original duration
        original_duration = get_duration(input_path)
        log(f"[PIPELINE] Original duration: {original_duration:.2f} seconds")

        # Silence removal stage
        current_percent = 10
        status_client.post_stage_changed(job_id, file_name, "Silence Removal", current_percent)
        
        clean_path = job_dir / "clean.mp4"
        log(f"[PIPELINE] Removing silence -> {clean_path}")
        remove_silence(
            input_path,
            clean_path,
            TMP_DIR,
            SILENCE_NOISE_DB,
            SILENCE_MIN_DURATION,
        )
        log(f"[PIPELINE] Clean video at {clean_path}")
        
        current_percent = 40
        status_client.post_progress(job_id, file_name, "Silence Removal", current_percent)

        # Clean duration
        clean_duration = get_duration(clean_path)
        time_removed = original_duration - clean_duration
        log(f"[PIPELINE] Clean duration: {clean_duration:.2f} seconds")
        log(f"[PIPELINE] Time removed: {time_removed:.2f} seconds")

        # Scene detection stage
        current_percent = 50
        status_client.post_stage_changed(job_id, file_name, "Scene Detection", current_percent)
        
        log(f"[SCENE] Running scene detection...")
        scenes_csv = run_scene_detect(clean_path, job_dir)
        log(f"[SCENE] Scene detection complete: {scenes_csv}")

        scenes = parse_scenes_csv(scenes_csv)
        log(f"[PIPELINE] Parsed {len(scenes)} scenes")
        
        current_percent = 70
        status_client.post_progress(job_id, file_name, "Scene Detection", current_percent)

        # Highlight extraction stage
        current_percent = 75
        status_client.post_stage_changed(job_id, file_name, "Highlight Extraction", current_percent)
        
        extract_highlights(clean_path, scenes, job_dir)
        
        current_percent = 90
        status_client.post_progress(job_id, file_name, "Highlight Extraction", current_percent)

        # Archive original
        current_percent = 95
        status_client.post_stage_changed(job_id, file_name, "Archiving", current_percent)
        
        ARCHIVE_DIR.mkdir(exist_ok=True)
        archived_path = ARCHIVE_DIR / input_path.name
        shutil.move(str(input_path), archived_path)
        log(f"[PIPELINE] Archived original file to {archived_path}")
        
        # Emit jobCompleted event
        status_client.post_completed(job_id, file_name)

    except Exception as e:
        log(f"[PIPELINE] ERROR: {e}")
        # Emit jobFailed event
        status_client.post_failed(job_id, file_name, str(e), current_percent)
        raise

    finally:
        # Stop resource monitor
        stop_monitor()

        # Summary
        total_time = time.time() - start_time
        avg_cpu = sum(samples["cpu"]) / len(samples["cpu"]) if samples["cpu"] else 0
        avg_ram = sum(samples["ram"]) / len(samples["ram"]) if samples["ram"] else 0

        log("")
        log("----- SUMMARY -----")
        log(f"Total processing time: {total_time:.2f} seconds")
        log(f"Average CPU usage: {avg_cpu:.1f}%")
        log(f"Average RAM usage: {avg_ram:.1f} MB")
        log(f"Original duration: {original_duration:.2f} seconds")
        log(f"Final duration: {clean_duration:.2f} seconds")
        log(f"Total time removed: {time_removed:.2f} seconds")
        log("--------------------")
        log("")

        log(f"[PIPELINE] Finished pipeline for {input_path}")
