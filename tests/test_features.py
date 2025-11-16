import numpy as np
from super_mario_motion.collect import extract_features
from super_mario_motion.vision_ml import _extract_features


def test_feature_extraction_match():
    rnd = np.random.default_rng(0)
    lm = rnd.random((33, 4), dtype=np.float32)
    feat_collect = extract_features(lm)
    feat_ml = _extract_features(lm)
    np.testing.assert_allclose(feat_collect, feat_ml, atol=1e-5)
