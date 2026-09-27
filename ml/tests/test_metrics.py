import numpy as np
from risk_engine.metrics import evaluate_binary, tune_threshold


def test_metrics_include_imbalance_metrics():
    y = np.array([0, 0, 0, 1, 1, 1])
    p = np.array([0.05, 0.2, 0.4, 0.65, 0.8, 0.95])
    m = evaluate_binary(y, p, 0.5)
    assert set(["precision", "recall", "f1", "roc_auc", "pr_auc", "confusion_matrix"]).issubset(m)
    assert len(m["confusion_matrix"]) == 2


def test_threshold_is_valid():
    t = tune_threshold([0, 0, 1, 1], [0.1, 0.3, 0.7, 0.9])
    assert 0.05 <= t <= 0.95
