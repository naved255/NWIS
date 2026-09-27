from __future__ import annotations
from typing import Dict, Optional
import numpy as np
from sklearn.metrics import (average_precision_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)


def evaluate_binary(y_true, probabilities, threshold: float) -> Dict:
    """Calculate imbalance-aware classification metrics at a chosen threshold."""
    y_pred = (np.asarray(probabilities) >= threshold).astype(int)
    y_true = np.asarray(y_true).astype(int)
    return {
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": _safe_auc(roc_auc_score, y_true, probabilities),
        "pr_auc": _safe_auc(average_precision_score, y_true, probabilities),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist(),
        "threshold": float(threshold),
        "support": int(len(y_true)),
    }


def _safe_auc(fn, y_true, scores) -> Optional[float]:
    try:
        return float(fn(y_true, scores))
    except ValueError:
        return None


def tune_threshold(y_true, probabilities, metric: str = "f1", target_recall: float = 0.8) -> float:
    """Tune a decision threshold on validation data only."""
    best_t, best_score = 0.5, -1.0
    for t in np.linspace(0.05, 0.95, 181):
        y_pred = (np.asarray(probabilities) >= t).astype(int)
        if metric == "recall":
            score = recall_score(y_true, y_pred, zero_division=0)
        else:
            recall = recall_score(y_true, y_pred, zero_division=0)
            if recall < target_recall:
                continue
            score = f1_score(y_true, y_pred, zero_division=0)
        if score > best_score:
            best_score, best_t = score, float(t)
    return best_t
