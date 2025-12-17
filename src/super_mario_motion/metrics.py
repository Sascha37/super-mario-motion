import os

from joblib import load

from super_mario_motion import path_helper as ph

_model = None

# Load model
try:
    model_path = ph.resource_path(
                os.path.join("data", "pose_model.joblib")
                )
    _model = load(model_path)
except Exception as e:
    print(f"Model not found {e}")

print(_model)