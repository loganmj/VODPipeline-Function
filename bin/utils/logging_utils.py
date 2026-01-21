from datetime import datetime

# Global variable set by run_pipeline.py
CURRENT_LOG_FILE = None

def set_log_file(path):
    global CURRENT_LOG_FILE
    CURRENT_LOG_FILE = path

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[PIPELINE] {timestamp} - {message}"

    # Always print to stdout (systemd captures this)
    print(line, flush=True)

    # Also write to per-job log file if set
    if CURRENT_LOG_FILE:
        with CURRENT_LOG_FILE.open("a") as f:
            f.write(line + "\n")
