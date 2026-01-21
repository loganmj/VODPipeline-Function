# VodPipeline

An automated pipeline for first-pass editing of VOD recordings. This tool watches for new video files, removes silence, detects scenes, and extracts highlights automatically.

## Features

- **Automated File Watching**: Monitors a directory for new MP4 files
- **Silence Removal**: Automatically removes silent portions from videos
- **Scene Detection**: Identifies scene changes in videos
- **Highlight Extraction**: Extracts the best highlights based on scene analysis
- **Resource Monitoring**: Tracks CPU and RAM usage during processing
- **Logging**: Comprehensive logging for each processed video

## System Requirements

- Python 3.10
- FFmpeg
- PySceneDetect
- Whisper.cpp (optional, for subtitle generation)
- Linux-based system (tested on Ubuntu/Debian)

## Quick Install

### 1. Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg python3 python3-pip python3-venv
```

### 2. Install PySceneDetect

```bash
pip install scenedetect[opencv]
```

### 3. Install Python Dependencies

```bash
pip install watchdog psutil
```

### 4. Install Whisper.cpp (Optional)

For subtitle generation support:

```bash
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
make
bash ./models/download-ggml-model.sh base.en
```

Update the paths in `bin/config.py` to point to your whisper.cpp installation.

### 5. Clone and Configure VodPipeline

```bash
git clone https://github.com/loganmj/VodPipeline.git
cd VodPipeline
```

Edit `bin/config.py` to configure your directories:

```python
INPUT_DIR = Path("/path/to/your/recordings")
EXPORT_BASE = Path("/path/to/output/complete")
TMP_DIR = Path("/path/to/tmp")
LOG_DIR = Path("/path/to/logs")
```

### 6. Create Required Directories

Create the directories you configured in the previous step:

```bash
# Replace these paths with the ones you configured in bin/config.py
mkdir -p /path/to/your/recordings
mkdir -p /path/to/output/complete
mkdir -p /path/to/tmp
mkdir -p /path/to/logs
```

## Usage

### Running the Pipeline

Start the file watcher:

```bash
python3 -m bin.vod_watcher
```

The watcher will monitor the `INPUT_DIR` for new MP4 files and automatically process them.

### Processing Workflow

1. A new MP4 file is detected in the input directory
2. The pipeline waits for the file to become stable (10 seconds without size change)
3. Silence is removed from the video
4. Scenes are detected in the cleaned video
5. Highlights are extracted based on scene analysis
6. The original file is archived
7. Results are saved to `EXPORT_BASE/{filename}/`

### Output Structure

For each processed video, the following directory structure is created:

```
EXPORT_BASE/
└── {video_name}/
    ├── clean.mp4              # Video with silence removed
    ├── pipeline.log           # Processing log
    ├── scenes/
    │   └── {video_name}-Scenes.csv # Scene detection data
    └── highlights/
        ├── highlight_01.mp4
        ├── highlight_02.mp4
        └── ...
```

## Configuration

Edit `bin/config.py` to customize:

- **Directories**: Input, output, temporary, and log paths
- **Silence Detection**: Noise threshold (`SILENCE_NOISE_DB`) and minimum duration (`SILENCE_MIN_DURATION`)
- **Highlight Extraction**: Maximum number (`MAX_HIGHLIGHTS`), minimum duration (`MIN_HIGHLIGHT_DURATION`), and maximum duration (`MAX_HIGHLIGHT_DURATION`)

## Running as a Service

To run VodPipeline as a systemd service:

1. Create a service file at `/etc/systemd/system/vod-pipeline.service` (replace `your-user` and `/path/to/VodPipeline` with your actual username and installation path):

```ini
[Unit]
Description=VOD Pipeline Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/VodPipeline
ExecStart=/usr/bin/python3 -m bin.vod_watcher
Restart=always

[Install]
WantedBy=multi-user.target
```

2. Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vod-pipeline
sudo systemctl start vod-pipeline
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
