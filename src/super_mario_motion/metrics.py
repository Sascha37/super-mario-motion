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

# Sample pose for standing
sample_standing = transform_landmarks(
        [[ 0.44344768,  0.12862258, -0.52724975,  0.9999959 ],
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
)

sample_crouching = transform_landmarks(
        [[ 0.4141589 ,  0.5229582 , -0.59570765,  0.99999595],
       [ 0.41702896,  0.5019441 , -0.5779897 ,  0.99999076],
       [ 0.4214796 ,  0.49975604, -0.5779791 ,  0.9999934 ],
       [ 0.42566967,  0.49757755, -0.5781208 ,  0.9999889 ],
       [ 0.39886767,  0.50870126, -0.58028173,  0.99998903],
       [ 0.39105707,  0.51154566, -0.580478  ,  0.99999106],
       [ 0.38428572,  0.51395375, -0.5805767 ,  0.99998343],
       [ 0.43121377,  0.50276494, -0.4472708 ,  0.99998844],
       [ 0.37210518,  0.52580744, -0.4562613 ,  0.9999882 ],
       [ 0.42577153,  0.5422162 , -0.54435414,  0.99999833],
       [ 0.40721983,  0.5504485 , -0.5469955 ,  0.99999785],
       [ 0.47875008,  0.5992901 , -0.36749205,  0.99996394],
       [ 0.33118945,  0.6115389 , -0.41273275,  0.9998446 ],
       [ 0.47437507,  0.7551978 , -0.39898148,  0.99166083],
       [ 0.34476608,  0.75825804, -0.45410386,  0.9920563 ],
       [ 0.44445643,  0.90134686, -0.48058748,  0.9931891 ],
       [ 0.3845655 ,  0.9210321 , -0.50603247,  0.98536676],
       [ 0.45280138,  0.9438291 , -0.528695  ,  0.983642  ],
       [ 0.37995568,  0.9671519 , -0.5542278 ,  0.9703078 ],
       [ 0.4350027 ,  0.95038575, -0.55318135,  0.9847895 ],
       [ 0.4015686 ,  0.96452177, -0.57358575,  0.9727912 ],
       [ 0.42784357,  0.9334356 , -0.49208206,  0.9860013 ],
       [ 0.40209237,  0.949513  , -0.5156566 ,  0.97415125],
       [ 0.43563527,  0.77988595,  0.0018728 ,  0.9999556 ],
       [ 0.35547248,  0.7790811 , -0.0020202 ,  0.99993265],
       [ 0.5238993 ,  0.78507334, -0.33957887,  0.9708933 ],
       [ 0.23212536,  0.8037713 , -0.35692278,  0.97481745],
       [ 0.45833555,  0.8749453 , -0.01005285,  0.8313998 ],
       [ 0.3324824 ,  0.87990636, -0.00484164,  0.76944   ],
       [ 0.45163593,  0.88441414,  0.02325876,  0.81576073],
       [ 0.3599527 ,  0.88190454,  0.03156534,  0.6687139 ],
       [ 0.50460136,  0.94679254, -0.03032129,  0.78488034],
       [ 0.3037199 ,  0.96223176, -0.02080463,  0.72154814]]
)
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
    return (correct/len(files))*100

def get_total_accuracy(labels, npy_dir):
    total_accuracy = 0
    for label in labels:
        total_accuracy += get_accuracy_for_label(label,npy_dir,False)
    return (total_accuracy/len(labels))

npy_path = ph.resource_path(
                os.path.join("..", "..", "tests", "npy")
                )

#print_probability(sample_crouching)
print(f"Average execution time: {get_average_execution_time(99, guess_most_likely, npy_path)} ms")
print(f"Acc standing:{get_accuracy_for_label("standing", npy_path, False)}")
print(f"Acc walking_left:{get_accuracy_for_label("walking_left", npy_path, True)}")
print(f"Combined accuracy:{get_total_accuracy(["standing", "walking_left"],npy_path)}")


