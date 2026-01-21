import os
from pathlib import Path

# Base paths
INPUT_DIR = Path("/mnt/pipeline/Recordings")
EXPORT_BASE = Path("/mnt/pipeline/VPipeline/Complete")
TMP_DIR = Path("/opt/vod-pipeline/tmp")
LOG_DIR = Path("/opt/vod-pipeline/logs")
ARCHIVE_DIR = INPUT_DIR / "Archive"

# Tools
FFMPEG_BIN = "ffmpeg"
SCENEDETECT_BIN = "scenedetect"
WHISPER_BIN = "/opt/whisper.cpp/build/bin/whisper-cli"  # adjust if needed
WHISPER_MODEL = "/opt/whisper.cpp/models/ggml-base.en.bin"

# Silence detection
SILENCE_NOISE_DB = -40  # dB -40 was best so far
SILENCE_MIN_DURATION = 1.5  # seconds 0.5 was best so far

# Highlight extraction
MAX_HIGHLIGHTS = 10
MIN_HIGHLIGHT_DURATION = 10.0  # seconds
MAX_HIGHLIGHT_DURATION = 90.0  # seconds
