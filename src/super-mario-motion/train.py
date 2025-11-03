import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
from joblib import dump

CSV_PATH = Path("../ml/pose_samples.csv")
MODEL_PATH = Path("../ml/pose_model.joblib")

def load_csv(csv_path: Path):
    labels, feats = [], []
    with open(csv_path, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 10:
                continue
            labels.append(parts[0])
            feats.append([float(x) for x in parts[1:]])
    X = np.array(feats, dtype=np.float32)
    y = np.array(labels)
    return X, y

def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"{CSV_PATH} nicht gefunden. Erst Daten mit collect.py sammeln.")

    X, y = load_csv(CSV_PATH)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
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
    gs.fit(X_train, y_train)

    print("Best params:", gs.best_params_)
    y_pred = gs.predict(X_test)
    print(classification_report(y_test, y_pred))
    print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))

    dump(gs.best_estimator_, MODEL_PATH)
    print(f"Saved model -> {MODEL_PATH}")

if __name__ == "__main__":
    main()