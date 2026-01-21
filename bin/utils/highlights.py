import subprocess
from pathlib import Path
from .logging_utils import log
from ..config import (
    MAX_HIGHLIGHTS,
    MIN_HIGHLIGHT_DURATION,
    MAX_HIGHLIGHT_DURATION,
)

def score_scene(start: float, end: float) -> float:
    # Simple heuristic: longer scenes score higher
    duration = end - start
    return duration

def select_highlights(scenes):
    scored = []
    for start, end in scenes:
        dur = end - start
        if dur < MIN_HIGHLIGHT_DURATION:
            continue
        if dur > MAX_HIGHLIGHT_DURATION:
            end = start + MAX_HIGHLIGHT_DURATION
        scored.append((score_scene(start, end), start, end))
    scored.sort(reverse=True)
    return [(s, e) for _, s, e in scored[:MAX_HIGHLIGHTS]]

def extract_highlights(clean_path: Path, scenes, job_dir: Path):
    # Create highlights subfolder
    highlights_dir = job_dir / "highlights"
    highlights_dir.mkdir(parents=True, exist_ok=True)

    highlights = select_highlights(scenes)
    results = []

    for idx, (start, end) in enumerate(highlights, start=1):
        duration = end - start
        out_path = highlights_dir / f"highlight_{idx:02d}.mp4"

        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-i", str(clean_path),      # input first
            "-ss", str(start),          # then seek
            "-t", str(duration),        # duration, not -to
            "-c:v", "libx264",          # re-encode video
            "-preset", "veryfast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-profile:v", "main",
            "-movflags", "+faststart",
            "-c:a", "aac",
            "-b:a", "192k",
            str(out_path),
        ]

        log(f"[HIGHLIGHT] Extracting: {' '.join(cmd)}")
        proc = subprocess.run(cmd)

        if proc.returncode == 0:
            results.append(out_path)
        else:
            log(f"[HIGHLIGHT] Failed for {out_path}")

    return results

