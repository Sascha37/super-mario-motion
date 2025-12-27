import os
import sys
import time
import glob
import random
import numpy as np
from joblib import load

from super_mario_motion import path_helper as ph
from super_mario_motion.pose_features import extract_features

_model = None


def transform_landmarks(landmarks):
    feat = extract_features(np.asarray(landmarks))
    return feat.reshape(1, -1)

# Load model
try:
    model_path = ph.resource_path(
                os.path.join("data", "pose_model.joblib")
                )
    _model = load(model_path)
except Exception as e:
    print(f"Model not found {e}")
    sys.exit(1)

def guess_most_likely(input):
    guesses = _model.predict_proba(input)[0]
    return _model.classes_[int(np.argmax(guesses))]

def print_probability(input):
    guesses = _model.predict_proba(input)[0]
    for i, prob in enumerate(guesses):
        guess = _model.classes_[i]
        print(f"{guess}, probability: {round(prob*100,2)}%")

def get_execution_time(func,input):
    t_start = time.perf_counter()
    func(input)
    t_stop = time.perf_counter()
    return (t_stop - t_start)*1000

# Average execution time across multiple runs, each time loading in a random numpy array
def get_average_execution_time(runs, func, npy_dir):
    files = glob.glob(os.path.join(npy_dir,"**","*.npy"), recursive=True)
    if not files:
        raise ValueError(f"[Metrics] no npy files found in: {npy_dir}")
    total_time = 0
    for _ in range(runs):
        file = random.choice(files)
        input_data = transform_landmarks(np.load(file))
        execution_time = get_execution_time(func, input_data)
        total_time += execution_time
    return total_time / runs

# Calculates the average accuracy for determening a specific label
def get_accuracy_for_label(expected, npy_dir, verbose):
    files = glob.glob(os.path.join(npy_dir,f"{expected}","*.npy"))
    if not files:
        raise ValueError(f"[Metrics] no {expected}-npy files found in: {npy_dir}")
    correct = 0
    for file in files:
        data = transform_landmarks(np.load(file))
        if verbose:
            print(file)
            print(guess_most_likely(data))
        if (guess_most_likely(data) == expected):
            correct += 1
    return round((correct/len(files))*100,2)

def get_total_accuracy(labels, npy_dir):
    total_accuracy = 0
    for label in labels:
        total_accuracy += get_accuracy_for_label(label,npy_dir,False)
    return round(total_accuracy/len(labels),2)

def get_file_size(path):
    return os.path.getsize(path)

npy_path = ph.resource_path(
                os.path.join("..", "..", "tests", "npy")
                )
def print_metric_report():
    separator_length = 35
    runs = 150
    labels = ["standing", "walking_left",
    "walking_right", "jumping", "running_right",
    "running_left","crouching", "throwing",
    "swimming"]

    print(f"#"*separator_length)
    print(f"Report for file: {model_path}\n")
    print(f"File size: {get_file_size(model_path)/1000000} MB")
    print(f"Average execution time across {runs} runs: {get_average_execution_time(runs, guess_most_likely, npy_path)} ms\n")
    print("Accuracy")
    for label in labels:
        print(f"{get_accuracy_for_label(label, npy_path, False)}% -- {label}")
    
    print(f"{get_total_accuracy(labels,npy_path)}% -- Total accuracy")
    print(f"#"*separator_length)
    
print_metric_report()


