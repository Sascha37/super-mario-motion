import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Full UI/camera startup test is skipped in CI environment.",
    )
def test_program_crashing():
    script = Path(__file__).parent.parent / "src/super_mario_motion/main.py"

    try:
        subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=7
            )
    except subprocess.TimeoutExpired:
        return

    assert False, "Program exited early — likely crashed during startup."
