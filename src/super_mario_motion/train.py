from pathlib import Path

import numpy as np
from joblib import dump
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

CSV_PATH = Path(__file__).parent.parent.parent / "data" / "pose_samples.csv"
MODEL_PATH = Path(__file__).parent.parent.parent / "data" / "pose_model.joblib"


def combine_run_csvs(output_name: str = "pose_samples_all.csv",
                     runs_subdir: str = "collect_runs",
                     pattern: str = "pose_samples_*.csv") -> Path:
    all_csvs = Path(__file__).parent.parent.parent / "data" / output_name
    if all_csvs.exists():
        (all_csvs.unlink())
    data_dir = Path(__file__).parent.parent.parent / "data"
    files = sorted(data_dir.glob(pattern))
    if not files:
        raise FileNotFoundError(f"Keine Collect-Dateien in {data_dir} gefunden.")
    out_path = data_dir / output_name
    with open(out_path, "w") as out_f:
        for i, fp in enumerate(files):
            with open(fp, "r") as in_f:
                for j, line in enumerate(in_f):
                    if i > 0 and j == 0 and line.lower().startswith("label,"):
                        continue
                    out_f.write(line)
    return out_path


def load_csv(csv_path: Path):
    labels, feats = [], []
    with open(csv_path, "r") as f:
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
    # if not CSV_PATH.exists():
    #    raise FileNotFoundError(f"{CSV_PATH} nicht gefunden. Erst Daten mit collect.py sammeln.")
    training_csv = combine_run_csvs()
    x, y = load_csv(training_csv)
    s_train, s_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, stratify=y, random_state=42
        )

    pipe = Pipeline([
        ("scaler", StandardScaler(with_mean=True)),
        ("pca", PCA(n_components=0.95, svd_solver="full")),  # optional; kannst du auch entfernen
        ("clf", SVC(probability=True))
        ])

    grid = {
        "clf__C": [0.5, 1, 2, 5],
        "clf__kernel": ["rbf", "linear"],
        "clf__gamma": ["scale", "auto"]
        }

    gs = GridSearchCV(pipe, grid, cv=5, n_jobs=-1, scoring="f1_weighted", verbose=1)
    gs.fit(s_train, y_train)

    print("Best params:", gs.best_params_)
    y_pred = gs.predict(s_test)
    print(classification_report(y_test, y_pred))
    print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))

    dump(gs.best_estimator_, MODEL_PATH)
    print(f"Saved model -> {MODEL_PATH}")


if __name__ == "__main__":
    main()
