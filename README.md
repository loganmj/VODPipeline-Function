# VODPipeline-Function

An automated pipeline for first-pass editing of VOD recordings. This tool watches for new video files, removes silence, detects scenes, and extracts highlights automatically.

## Related Repositories

This is the function/processing component of the VODPipeline application. For the complete system, see also:

- **UI**: [VODPipeline-UI](https://github.com/loganmj/VODPipeline-UI) - User interface for managing and viewing processed videos
- **API**: [VODPipeline-API](https://github.com/loganmj/VODPipeline-API) - Backend API for the VODPipeline system

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

### 5. Clone and Configure VODPipeline-Function

```bash
git clone https://github.com/loganmj/VODPipeline-Function.git
cd VODPipeline-Function
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
- **API Integration**: Set the `API_BASE_URL` environment variable to enable job status events (e.g., `export API_BASE_URL=http://localhost:5000`)
- **Status Server**: Set the `STATUS_SERVER_PORT` environment variable to configure the status endpoint port (default: 8080)

### Job Status Events

The pipeline emits job status events to the configured API endpoint throughout the processing lifecycle:

- **jobStarted**: Sent when processing begins
- **jobStageChanged**: Sent when entering a new processing stage (Silence Removal, Scene Detection, Highlight Extraction, Archiving)
- **jobProgressUpdated**: Sent periodically during processing to report progress
- **jobCompleted**: Sent when processing completes successfully
- **jobFailed**: Sent if an error occurs during processing

Each event includes:
- Unique job ID (UUID)
- File name
- Current stage
- Progress percentage (0-100)
- UTC timestamp
- Error message (for failures only)

#### Event Emission API

The pipeline provides a unified `emit_event()` method in the `JobStatusClient` that handles:
1. Updating internal state
2. Building the appropriate JobStatus DTO
3. POSTing to the API
4. Handling transient failures gracefully

**Example Usage**:
```python
from bin.clients.job_status_client import JobStatusClient

client = JobStatusClient(api_base_url="http://localhost:5000")

# Job started
client.emit_event(job_id, file_name, "Starting", 0)

# Stage changed
client.emit_event(job_id, file_name, "Silence Removal", 10)

# Progress update
client.emit_event(job_id, file_name, "Silence Removal", 40)

# Job completed
client.emit_event(job_id, file_name, "Completed", 100)

# Job failed
client.emit_event(job_id, file_name, "Failed", 35, error_message="Processing error")
```

The method automatically determines the event type based on the stage name and the current state, emitting the appropriate event (jobStarted, jobStageChanged, jobProgressUpdated, jobCompleted, or jobFailed).

To enable API communication, set the `API_BASE_URL` environment variable:

```bash
export API_BASE_URL=http://localhost:5000
python3 -m bin.vod_watcher
```

If `API_BASE_URL` is not set or is empty, the pipeline will run without API communication.

### Status Endpoint

The Function exposes a status endpoint that allows external systems (such as the API) to request the current job status. This is useful for establishing a base state when the UI is launched or refreshed.

**Endpoint**: `GET /status`

**Default Port**: 8080 (configurable via `STATUS_SERVER_PORT` environment variable)

**Example Request**:
```bash
curl http://localhost:8080/status
```

**Example Response** (when a job is running):
```json
{
  "jobId": "550e8400-e29b-41d4-a716-446655440000",
  "fileName": "video.mp4",
  "stage": "Silence Removal",
  "percent": 42,
  "timestamp": "2026-01-26T17:45:00Z",
  "errorMessage": null
}
```

**Example Response** (when idle):
```json
{
  "jobId": null,
  "fileName": null,
  "stage": "Idle",
  "percent": 0,
  "timestamp": "2026-01-26T17:45:00Z",
  "errorMessage": null
}
```

**Example Response** (when failed):
```json
{
  "jobId": "550e8400-e29b-41d4-a716-446655440000",
  "fileName": "video.mp4",
  "stage": "Failed",
  "percent": 30,
  "timestamp": "2026-01-26T17:45:00Z",
  "errorMessage": "Error processing file"
}
```

The status endpoint:
- Returns the current job snapshot (not an event)
- Never blocks
- Always returns UTC timestamps
- Returns "Idle" state when no job is running or when a job has completed successfully
- Preserves "Failed" state until the next job starts

To configure the status server port:

```bash
export STATUS_SERVER_PORT=9000
python3 -m bin.vod_watcher
```

## Running as a Service

To run VODPipeline-Function as a systemd service:

1. Create a service file at `/etc/systemd/system/vod-pipeline.service` (replace `your-user` and `/path/to/VODPipeline-Function` with your actual username and installation path):

```ini
[Unit]
Description=VOD Pipeline Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/VODPipeline-Function
ExecStart=/usr/bin/python3 -m bin.vod_watcher
Restart=always
Environment="API_BASE_URL=http://localhost:5000"
Environment="STATUS_SERVER_PORT=8080"

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
