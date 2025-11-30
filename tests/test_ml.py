import numpy as np
import csv
from pathlib import Path
import pytest

from super_mario_motion.collect import extract_features

LABELS = [
    "standing", "walking_left", "running_left", "walking_right",
    "running_right", "jumping", "crouching", "throwing", "swimming"
    ]


# test if the feature shape and type are correct
def test_feature_shape_and_type():
    lm = np.random.rand(33, 4).astype(np.float32)
    features = extract_features(lm)

    assert features.shape == (109,)
    assert features.dtype == np.float32
    assert np.all(np.isfinite(features))


def test_training_csv_integrity():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    files = list(data_dir.glob("pose_samples*.csv"))

    if not files:
        pytest.skip("No training data CSVs found – skipping integrity check.")

    for file in files:
        with file.open() as f:
            reader = csv.reader(f)
            for row in reader:
                # Row length check
                assert len(row) == 110, f"Invalid row length in {file}: {len(row)}"

                # Label check
                label = row[0]
                assert label in LABELS, f"Invalid label '{label}' in {file}"

                # Feature check
                features = np.array(row[1:], dtype=np.float32)

                # All values are finite
                assert np.all(np.isfinite(features)), f"Non-finite values in {file}"

                # Features are numeric
                assert features.dtype == np.float32
