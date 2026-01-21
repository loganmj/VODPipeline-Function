import subprocess
from pathlib import Path
from .logging_utils import log
from ..config import WHISPER_BIN, WHISPER_MODEL

def generate_subtitles(clean_path: Path, out_dir: Path, base_name: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    out_prefix = out_dir / base_name
    cmd = [
        WHISPER_BIN,
        "-m", WHISPER_MODEL,
        "-f", str(clean_path),
        "-otxt",
        "-osrt",
        "-of", str(out_prefix),
    ]
    log(f"[SUBS] Running: {' '.join(cmd)}")
    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise RuntimeError("whisper failed")
    return out_prefix.with_suffix(".srt")
