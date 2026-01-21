#!/usr/bin/env python3
import time
import os
import threading
from queue import Queue
from pathlib import Path

from watchdog.observers.polling import PollingObserverVFS
from watchdog.events import FileSystemEventHandler

from bin.config import INPUT_DIR
from bin.utils.logging_utils import log
from bin.pipeline.run_pipeline import run_for_file


# Global job queue and tracking set
job_queue: "Queue[Path]" = Queue()
queued_files: set[Path] = set()
queue_lock = threading.Lock()


def wait_until_stable(path: Path, stable_seconds: int = 10) -> None:
    """Wait indefinitely until file size stops changing for stable_seconds."""
    last_size = -1
    stable_time = 0

    while True:
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            time.sleep(1)
            continue

        if size == last_size:
            stable_time += 1
            if stable_time >= stable_seconds:
                return
        else:
            stable_time = 0
            last_size = size

        time.sleep(1)


def worker_loop() -> None:
    """Worker that processes one file at a time from the queue."""
    log("[QUEUE] Worker thread started")

    while True:
        path = job_queue.get()
        try:
            log(f"[QUEUE] Dequeued job: {path}")
            run_for_file(path)
            log(f"[QUEUE] Finished job: {path}")
        except Exception as e:
            log(f"[QUEUE] Error while processing {path}: {e}")
        finally:
            with queue_lock:
                queued_files.discard(path)
            job_queue.task_done()


class VODHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)
        if path.suffix.lower() != ".mp4":
            return

        log(f"[WATCHER] New file detected: {path}")
        log("[WATCHER] Waiting for file to stabilize...")

        wait_until_stable(path, stable_seconds=10)

        with queue_lock:
            if path in queued_files:
                log(f"[QUEUE] File already queued, skipping duplicate: {path}")
                return
            queued_files.add(path)
            job_queue.put(path)
            log(f"[QUEUE] Enqueued job: {path}")


def main() -> None:
    log(f"[WATCHER] Starting watcher on {INPUT_DIR}")

    # Start the single worker thread
    worker = threading.Thread(target=worker_loop, daemon=True)
    worker.start()

    event_handler = VODHandler()

    observer = PollingObserverVFS(
        stat=os.stat,
        listdir=os.scandir,
    )

    observer.schedule(event_handler, str(INPUT_DIR), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("[WATCHER] KeyboardInterrupt received, stopping observer...")
        observer.stop()

    observer.join()
    log("[WATCHER] Observer stopped")


if __name__ == "__main__":
    main()
