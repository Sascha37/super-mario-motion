"""
Train and evaluate the pose classification model from collected CSV data.

Combines multiple run CSVs, loads features/labels, performs a train/test
split, runs a PCA+SVM pipeline with hyperparameter search, prints metrics,
and saves the best estimator to disk.
"""

from pathlib import Path

import numpy as np
from joblib import dump
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from super_mario_motion import user_data
from super_mario_motion.state import StateManager

# StateManager
state_manager = StateManager()

user_data.init()

data_path = state_manager.get_data_folder_path()

CSV_PATH = Path(data_path)
MODEL_PATH = Path(data_path) / "pose_model.joblib"
NUMBER_OF_ELEMENTS_PER_LINE = 110


def combine_run_csvs(
    output_name: str = "pose_samples_all.csv",
    pattern: str = "pose_samples_*.csv"
        ) -> Path:
    """Combine multiple collected run CSVs into a single CSV file.

    Existing output file is removed first. Header rows in the following files
    (starting with "label,") are skipped.

    Args:
        output_name: Name of the combined CSV file to create.
        pattern: Glob pattern for input CSVs in the data directory.

    Returns:
        Path: Full path to the combined CSV file.

    Raises:
        FileNotFoundError: If no matching input CSV files are found.
    """
    all_csvs = Path(data_path) / output_name
    if all_csvs.exists():
        (all_csvs.unlink())
    data_dir = Path(data_path)
    files = sorted(data_dir.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No collect-files found in {data_dir}.")
    out_path = data_dir / output_name
    with open(out_path, "w") as out_f:
        for i, fp in enumerate(files):
            with open(fp) as in_f:
                for j, line in enumerate(in_f):
                    if i > 0 and j == 0 and line.lower().startswith("label,"):
                        continue
                    out_f.write(line)
    return out_path


def load_csv(csv_path: Path):
    labels, feats = [], []
    with open(csv_path) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < NUMBER_OF_ELEMENTS_PER_LINE:
                continue
            labels.append(parts[0])
            feats.append([float(x) for x in parts[1:]])
    x = np.array(feats, dtype=np.float32)
    y = np.array(labels)
    return x, y



def main():
    # Check if CSV files exists. If so, concatenate them
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"{CSV_PATH} not found. Collect data first"
            f" with collect.py."
            )
    training_csv = combine_run_csvs()
    x, y = load_csv(training_csv)

    # drop samples with low average visibilities
    n_vis = 33
    vis = x[:, -n_vis:]
    mask = np.mean(vis, axis=1) > 0.6
    x = x[mask]
    y = y[mask]

    s_train, s_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, stratify=y, random_state=42
        )

    pipe = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", SVC(
                kernel="linear",
                C=5.0,
                gamma="scale",
                probability=True,
                class_weight="balanced"
            ))
            ]
        )


    pipe.fit(s_train, y_train)

    y_pred = pipe.predict(s_test)

    print(classification_report(y_test, y_pred))
    print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))

    dump(pipe, MODEL_PATH)
    print(f"Saved model -> {MODEL_PATH}")


if __name__ == "__main__":
    main()
