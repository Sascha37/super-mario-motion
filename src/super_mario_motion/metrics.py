import os
import sys
import time
import numpy as np
from joblib import load

from super_mario_motion import path_helper as ph
from super_mario_motion.pose_features import extract_features

_model = None

# Sample pose for standing

sample_landmarks = [[ 0.44344768,  0.12862258, -0.52724975,  0.9999959 ],
       [ 0.4466985 ,  0.11005745, -0.5054582 ,  0.9999868 ],
       [ 0.45136994,  0.1095399 , -0.505459  ,  0.99998677],
       [ 0.45602483,  0.10892276, -0.50542736,  0.9999852 ],
       [ 0.43058357,  0.11243799, -0.5089975 ,  0.9999866 ],
       [ 0.4233316 ,  0.11433233, -0.50905764,  0.99998564],
       [ 0.41663846,  0.11643733, -0.509061  ,  0.9999836 ],
       [ 0.4602335 ,  0.11720481, -0.34139615,  0.99997574],
       [ 0.4047501 ,  0.12935439, -0.36131   ,  0.9999774 ],
       [ 0.45178992,  0.14958182, -0.46341276,  0.9999948 ],
       [ 0.4329864 ,  0.15187655, -0.4689719 ,  0.9999953 ],
       [ 0.512822  ,  0.23516212, -0.21798329,  0.9999926 ],
       [ 0.3629361 ,  0.23708993, -0.22907202,  0.9999713 ],
       [ 0.54174834,  0.3700427 , -0.13230371,  0.9972902 ],
       [ 0.31271082,  0.3722936 , -0.16662258,  0.9934234 ],
       [ 0.5592684 ,  0.48856434, -0.2794969 ,  0.9964595 ],
       [ 0.31442192,  0.4957097 , -0.28236943,  0.9759344 ],
       [ 0.5674053 ,  0.53086895, -0.3222738 ,  0.9900075 ],
       [ 0.30900994,  0.541054  , -0.31982186,  0.9448821 ],
       [ 0.557729  ,  0.5289269 , -0.37300414,  0.9909826 ],
       [ 0.32432017,  0.53854233, -0.36410803,  0.9480987 ],
       [ 0.55235636,  0.51966864, -0.30123785,  0.9887328 ],
       [ 0.33007738,  0.5258046 , -0.30183846,  0.9427147 ],
       [ 0.47750145,  0.51038295,  0.00584173,  0.9996266 ],
       [ 0.39341128,  0.5133024 , -0.005853  ,  0.9996829 ],
       [ 0.47891116,  0.70021284,  0.06103351,  0.98793465],
       [ 0.40057343,  0.7106213 ,  0.02663944,  0.9910053 ],
       [ 0.48717833,  0.876327  ,  0.28737706,  0.9865153 ],
       [ 0.40084133,  0.88478154,  0.25811908,  0.9829772 ],
       [ 0.48047763,  0.8985415 ,  0.29923075,  0.89630115],
       [ 0.40416384,  0.9024896 ,  0.2710532 ,  0.8190876 ],
       [ 0.5093587 ,  0.9507483 ,  0.12808432,  0.9774671 ],
       [ 0.3897793 ,  0.9632971 ,  0.08934968,  0.9676652 ]]
a = np.load("/home/sascha/Documents/teamprojekt/aa/super-mario-motion/landmark_standing6.npy")
print(a)
# Load model
try:
    model_path = ph.resource_path(
                os.path.join("data", "pose_model.joblib")
                )
    _model = load(model_path)
except Exception as e:
    print(f"Model not found {e}")
    sys.exit(1)

def transform_landmarks(landmarks):
    feat = extract_features(np.asarray(landmarks))
    return feat.reshape(1, -1)

def guess_most_likely(input):
    guesses = _model.predict_proba(input)[0]
    return _model.classes_[int(np.argmax(guesses))]

def print_all_guesses(input):
    guesses = _model.predict_proba(input)[0]
    for i, prob in enumerate(guesses):
        guess = _model.classes_[i]
        print(f"{guess}, probability: {round(prob*100,2)}%")

# TODO use random input
def get_average_execution_time(runs, func, input):
    total_time = 0
    for n in range(runs):
        t_start = time.perf_counter()
        func(input)
        t_stop = time.perf_counter()
        total_time += (t_stop - t_start)*1000
    return total_time / n

def get_accuracy(expected, dataset):
    correct = 0
    for i,data in enumerate(dataset):
        if (guess_most_likely(data) == expected):
            correct += 1
    return (correct/(i+1))*100

transformed_landmarks = transform_landmarks(a)

print_all_guesses(transformed_landmarks)
print(f"Average execution time: {get_average_execution_time(99, guess_most_likely, transformed_landmarks)} ms")
print(f"Acc:{get_accuracy("standing", [transformed_landmarks,transformed_landmarks,transformed_landmarks])}")