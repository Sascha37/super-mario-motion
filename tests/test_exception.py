import subprocess
import sys
from pathlib import Path


def test_program_starts_without_crashing():
    script = Path(__file__).parent.parent / "src/super_mario_motion/main.py"

    try:
        subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=5
            )
    except subprocess.TimeoutExpired:
        return

    assert False, "Program exited early — likely crashed during startup."
