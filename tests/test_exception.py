"""
Test that the main application script fails with an exception and emits
a traceback when executed as a subprocess.
"""

import subprocess
import sys
from pathlib import Path


def test_program_throws_exception():
    script = Path(__file__).parent.parent / "src/super_mario_motion/main.py"

    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True
        )

    # assert that it failed
    assert result.returncode != 0

    # check error message
    assert "Traceback" in result.stderr
