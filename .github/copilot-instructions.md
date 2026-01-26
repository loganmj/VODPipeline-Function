# GitHub Copilot Coding Agent Instructions

## Project Overview
VODPipeline-Function is an automated pipeline for first-pass editing of VOD (Video on Demand) recordings. This tool watches for new video files, removes silence, detects scenes, and extracts highlights automatically.

## Tech Stack
- **Python**: 3.10+
- **Key Dependencies**:
  - `watchdog`: File system monitoring
  - `psutil`: Resource monitoring
  - `ffmpeg`: Video processing (system dependency)
  - `scenedetect[opencv]`: Scene detection (PySceneDetect)
  - `whisper.cpp`: Optional subtitle generation
- **Testing**: pytest with pytest-cov

## Project Structure
- `bin/`: Main application code
  - `config.py`: Configuration settings
  - `vod_watcher.py`: File watcher entry point
  - `pipeline/`: Pipeline execution logic
  - `utils/`: Utility modules (silence removal, scene detection, highlights, subtitles)
  - `clients/`: API clients (job status)
  - `models/`: Data models (job status)
- `tests/`: Unit tests

## Build & Test Commands

### Running Tests
```bash
python -m pytest tests/ -v --tb=short
```

### Running the Application
```bash
python3 -m bin.vod_watcher
```

### Build/Compile Check
```bash
python -m compileall . -q
```

## Code Style & Conventions

### Python Standards
- Use Python 3.10+ features (type hints with `|` syntax, match statements if appropriate)
- Use type hints for all function parameters and return types
- Use `Path` objects from `pathlib` for file system paths, not strings
- Follow PEP 8 naming conventions

### Type Hints
```python
# Good
def process_video(path: Path, max_highlights: int = 10) -> dict[str, Any]:
    pass

# Bad
def process_video(path, max_highlights=10):
    pass
```

### Error Handling
- Use try-except blocks for file operations and external tool calls
- Log errors using the `bin.utils.logging_utils.log()` function
- Return meaningful error messages

### Logging
- Use the centralized logging utility: `from bin.utils.logging_utils import log`
- Include context in log messages: `log(f"[STAGE_NAME] Message")`
- Follow the existing `log()` formatting; log levels are not currently supported, so include level/context keywords in the message text if needed (e.g., `log("[ERROR][STAGE_NAME] Message")`)

## Configuration
- All configuration should be in `bin/config.py`
- Use `Path` objects for directory paths
- Support environment variables for runtime configuration (e.g., `API_BASE_URL`)
- Never hardcode paths or credentials

## File/Directory Exclusions
- **Never modify**: `/dist`, `/build`, `__pycache__`, `.git`
- **Do not commit**: `.env` files, secrets, API keys, credentials
- **Do not modify system paths**: System-level dependencies like FFmpeg, Whisper.cpp installations

## Testing Guidelines
- Write tests for new utility functions and business logic
- Place tests in `tests/` directory with `test_` prefix
- Use pytest fixtures for common setup
- Mock external dependencies (FFmpeg, API calls, file system operations where appropriate)
- Maintain existing test structure and patterns

## Dependencies
- Use existing dependencies when possible
- If adding new dependencies, ensure they are:
  - Well-maintained and actively developed
  - Compatible with Python 3.10+
  - Added to appropriate requirements file (if one exists or is created)
  - Documented in README.md if they require system-level installation

## API Integration
- The pipeline can optionally send job status events to an API endpoint
- API communication is configured via `API_BASE_URL` environment variable
- Always handle API communication failures gracefully (pipeline should work without API)
- Use the `JobStatusClient` from `bin.clients.job_status_client` for API communication

## Video Processing Notes
- The pipeline uses FFmpeg for video operations - ensure commands are safe and validated
- Scene detection uses PySceneDetect - respect existing threshold configurations
- Silence removal parameters are tuned in config.py - changes should be tested
- Output directory structure must be maintained for compatibility with VODPipeline-UI and VODPipeline-API

## Examples

### Adding a New Utility Function
```python
# Good: Type hints, error handling, logging
from pathlib import Path
from typing import Any
from bin.utils.logging_utils import log

def extract_metadata(video_path: Path) -> dict[str, Any]:
    """Extract metadata from video file using FFmpeg."""
    try:
        log(f"[METADATA] Extracting metadata from {video_path.name}")
        # Implementation here
        return metadata
    except Exception as e:
        log(f"[METADATA] Error: {e}")
        raise
```

### Configuration Pattern
```python
# Good: Use config.py constants
from bin.config import TMP_DIR, FFMPEG_BIN

temp_file = TMP_DIR / "processing.mp4"
cmd = [FFMPEG_BIN, "-i", str(input_path), str(output_path)]

# Bad: Hardcoded paths and tool names
temp_file = "/tmp/processing.mp4"
cmd = ["ffmpeg", "-i", input_path, output_path]
```

## Commit Guidelines
- Write clear, descriptive commit messages
- Reference related issues if applicable
- Keep commits focused on a single change or feature

## Related Repositories
This is part of a larger system:
- **VODPipeline-UI**: User interface for managing videos
- **VODPipeline-API**: Backend API for the system

Changes that affect data formats, API contracts, or output structure should consider compatibility with these components.
