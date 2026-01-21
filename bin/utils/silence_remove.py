import time
import re
import subprocess
from pathlib import Path
from .logging_utils import log

SILENCE_START_RE = re.compile(r"silence_start:\s*([0-9.]+)")
SILENCE_END_RE = re.compile(r"silence_end:\s*([0-9.]+)")

# Padding around each segment to prevent clipped speech
SEGMENT_PADDING = 0.15


def run_ffmpeg_silencedetect(input_path: Path, log_path: Path, noise_db: int, min_dur: float):
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-i", str(input_path),
        "-af", f"silencedetect=noise={noise_db}dB:d={min_dur}",
        "-f", "null",
        "-",
    ]
    log(f"[SILENCE] Running: {' '.join(cmd)}")
    with log_path.open("w") as lf:
        proc = subprocess.run(cmd, stderr=lf, stdout=subprocess.DEVNULL)
    if proc.returncode != 0:
        log(f"[SILENCE] ffmpeg silencedetect failed with code {proc.returncode}")
        raise RuntimeError("silencedetect failed")


def parse_silence_log(log_path: Path, total_duration: float):
    starts = []
    ends = []
    with log_path.open() as f:
        for line in f:
            m_start = SILENCE_START_RE.search(line)
            if m_start:
                starts.append(float(m_start.group(1)))
            m_end = SILENCE_END_RE.search(line)
            if m_end:
                ends.append(float(m_end.group(1)))

    segments = []
    current = 0.0

    for s, e in zip(starts, ends):
        if s > current:
            seg_start = max(0.0, current - SEGMENT_PADDING)
            seg_end = min(s + SEGMENT_PADDING, total_duration)
            segments.append((seg_start, seg_end))
        current = e

    if current < total_duration:
        seg_start = max(0.0, current - SEGMENT_PADDING)
        seg_end = total_duration
        segments.append((seg_start, seg_end))

    return segments


def get_duration(input_path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(input_path),
    ]

    while True:
        try:
            out = subprocess.check_output(cmd, text=True).strip()
            return float(out)
        except subprocess.CalledProcessError as e:
            log(f"[SILENCE] ffprobe failed ({e.returncode}), retrying in 5s...")
            time.sleep(5)
        except FileNotFoundError:
            log("[SILENCE] Input file disappeared, retrying in 5s...")
            time.sleep(5)


def write_concat_file(segments, concat_path: Path, input_path: Path):
    with concat_path.open("w") as f:
        for start, end in segments:
            f.write(f"file '{input_path}'\n")
            f.write(f"inpoint {start}\n")
            f.write(f"outpoint {end}\n")


def build_clean_video(input_path: Path, output_path: Path, segments):
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile("w", suffix=".txt", delete=False) as tf:
        concat_path = Path(tf.name)

    write_concat_file(segments, concat_path, input_path)

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_path),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-profile:v", "main",
        "-movflags", "+faststart",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path),
    ]

    log(f"[SILENCE] Building clean video (re-encode): {' '.join(cmd)}")
    proc = subprocess.run(cmd)
    concat_path.unlink(missing_ok=True)

    if proc.returncode != 0:
        raise RuntimeError("ffmpeg concat re-encode failed")


def remove_silence(input_path: Path, output_path: Path, tmp_dir: Path, noise_db: int, min_dur: float):
    tmp_dir.mkdir(parents=True, exist_ok=True)
    silence_log = tmp_dir / "silence.log"

    duration = get_duration(input_path)
    run_ffmpeg_silencedetect(input_path, silence_log, noise_db, min_dur)

    segments = parse_silence_log(silence_log, duration)
    if not segments:
        log("[SILENCE] No segments found, copying input")
        subprocess.run(["cp", str(input_path), str(output_path)], check=True)
        return

    build_clean_video(input_path, output_path, segments)
