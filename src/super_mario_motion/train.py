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

CSV_PATH = Path(__file__).parent.parent.parent / "data"
MODEL_PATH = Path(__file__).parent.parent.parent / "data" / "pose_model.joblib"


def combine_run_csvs(
        output_name: str = "pose_samples_all.csv",
        pattern: str = "pose_samples_*.csv"
        ) -> Path:
    """Combine multiple collected run CSVs into a single CSV file.

    Existing output file is removed first. Header rows in the following files
    (starting with 'label,') are skipped.

    Args:
        output_name: Name of the combined CSV file to create.
        pattern: Glob pattern for input CSVs in the data directory.

    Returns:
        Path: Full path to the combined CSV file.

    Raises:
        FileNotFoundError: If no matching input CSV files are found.
    """
    all_csvs = Path(__file__).parent.parent.parent / "data" / output_name
    if all_csvs.exists():
        (all_csvs.unlink())
    data_dir = Path(__file__).parent.parent.parent / "data"
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
    """Load features and labels from a pose-sample CSV file.

    Expects the first column to be the label and the remaining columns to
    be floating-point feature values.

    Args:
        csv_path: Path to the CSV file.

    Returns:
        tuple[np.ndarray, np.ndarray]:
            x: Feature matrix of shape (n_samples, n_features), dtype float32.
            y: Label array of shape (n_samples), dtype object/str.
    """
    labels, feats = [], []
    with open(csv_path) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 10:
                continue
            labels.append(parts[0])
            feats.append([float(x) for x in parts[1:]])
    x = np.array(feats, dtype=np.float32)
    y = np.array(labels)
    return x, y


def main():
    """Train and evaluate the pose classifier, then save the best model.

    Steps:
      * Combine all run CSV files.
      * Load feature matrix X and labels y.
      * Split into train/test sets with stratification.
      * Build a pipeline: StandardScaler -> PCA (95% var) -> SVC.
      * Run GridSearchCV over SVC hyperparameters (C, kernel, gamma).
      * Print best parameters, classification report and confusion matrix.
      * Save the best estimator to MODEL_PATH.
    """
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"{CSV_PATH} not found. Collect data first"
            f" with collect.py."
            )
    training_csv = combine_run_csvs()
    x, y = load_csv(training_csv)
    s_train, s_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, stratify=y, random_state=42
        )

    pipe = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("pca", PCA(n_components=0.95, svd_solver="full")),
            # optional, can be removed
            ("clf", SVC(probability=True))
            ]
        )

    grid = {
        "clf__C": [0.5, 1, 2, 5],
        "clf__kernel": ["rbf", "linear"],
        "clf__gamma": ["scale", "auto"]
        }

    gs = GridSearchCV(
        pipe, grid, cv=5, n_jobs=-1, scoring="f1_weighted",
        verbose=1
        )
    gs.fit(s_train, y_train)

    print("Best params:", gs.best_params_)
    y_pred = gs.predict(s_test)
    print(classification_report(y_test, y_pred))
    print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))

    dump(gs.best_estimator_, MODEL_PATH)
    print(f"Saved model -> {MODEL_PATH}")


if __name__ == "__main__":
    main()
