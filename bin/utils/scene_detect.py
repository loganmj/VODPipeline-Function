import subprocess
from pathlib import Path
from .logging_utils import log


def run_scene_detect(input_path: Path, job_dir: Path) -> Path:
    """
    Runs PySceneDetect on the given input video and returns the path
    to the generated Scenes CSV file.
    """
    scenes_dir = job_dir / "scenes"
    scenes_dir.mkdir(exist_ok=True)

    csv_path = scenes_dir / f"{input_path.stem}-Scenes.csv"

    cmd = [
        "/root/.local/bin/scenedetect",
        "-i", str(input_path),
        "-o", str(scenes_dir),
        "detect-content",
        "list-scenes",
    ]

    log(f"[SCENE] Running: {' '.join(cmd)}")

    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if proc.returncode != 0:
        log(f"[SCENE] scenedetect failed with exit code {proc.returncode}")
        log(f"[SCENE] stdout: {proc.stdout}")
        log(f"[SCENE] stderr: {proc.stderr}")
        raise RuntimeError("Scene detection failed")

    if not csv_path.exists():
        raise RuntimeError(f"Scene CSV not found at {csv_path}")

    return csv_path


def parse_scenes_csv(csv_path: Path):
    """
    Parses a PySceneDetect 0.6.x Scenes CSV file and returns a list of
    (start_time, end_time) tuples in seconds.

    CSV columns:
    0: Scene Number
    1: Start Timecode
    2: Start Frame
    3: Start Time (seconds)
    4: End Timecode
    5: End Frame
    6: End Time (seconds)
    """
    scenes = []

    with csv_path.open() as f:
        header = True
        for line in f:
            if header:
                header = False
                continue

            parts = line.strip().split(",")

            if len(parts) < 7:
                continue

            try:
                start = float(parts[3])
                end = float(parts[6])
                scenes.append((start, end))
            except ValueError:
                continue

    return scenes
