"""
Benchmark metrics for model performance analysis.
Measures: latency, FPR, FNR, number of rules.
"""

import time
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

from config import FEATURE_NAMES


def measure_inference_latency(model, X_test: np.ndarray, n_warmup: int = 10) -> Dict[str, float]:
    """
    Measure inference latency per sample.

    Args:
        model: Trained model with .predict() method
        X_test: Test features (N, num_features)
        n_warmup: Number of warmup iterations to exclude from timing

    Returns:
        Dict with: mean_latency_ms, p50_latency_ms, p95_latency_ms, p99_latency_ms
    """
    # Warmup
    for _ in range(n_warmup):
        _ = model.predict(X_test[:1])

    latencies = []
    for sample in X_test:
        start = time.perf_counter()
        _ = model.predict(sample.reshape(1, -1))
        end = time.perf_counter()
        latencies.append((end - start) * 1000)  # convert to ms

    latencies = np.array(latencies)

    return {
        "mean_latency_ms": float(np.mean(latencies)),
        "p50_latency_ms": float(np.percentile(latencies, 50)),
        "p95_latency_ms": float(np.percentile(latencies, 95)),
        "p99_latency_ms": float(np.percentile(latencies, 99)),
    }


def measure_false_rates(y_test: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Measure False Positive Rate (FPR) and False Negative Rate (FNR).

    Args:
        y_test: True labels (0=benign, 1=attack)
        y_pred: Predicted labels

    Returns:
        Dict with: fpr, fnr, true_positive_rate, true_negative_rate
    """
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    # FPR = FP / (FP + TN) = false positive / all actual negatives
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    # FNR = FN / (FN + TP) = false negative / all actual positives
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    # TPR = TP / (TP + FN)
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    # TNR = TN / (TN + FP)
    tnr = tn / (tn + fp) if (tn + fp) > 0 else 0.0

    return {
        "fpr": float(fpr),
        "fnr": float(fnr),
        "tpr": float(tpr),
        "tnr": float(tnr),
        "tp": int(tp),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
    }


def count_decision_tree_rules(tree_obj) -> int:
    """
    Count number of decision rules (leaf nodes) in a decision tree.
    Each unique path from root to leaf = 1 rule.

    Args:
        tree_obj: sklearn DecisionTreeClassifier or repo DT-CTS model

    Returns:
        Number of rules (leaf nodes)
    """
    if hasattr(tree_obj, "tree_"):
        # sklearn tree
        tree = tree_obj.tree_

        def count_leaves(node_id):
            if tree.feature[node_id] == -2:  # leaf node
                return 1
            left_count = count_leaves(tree.children_left[node_id])
            right_count = count_leaves(tree.children_right[node_id])
            return left_count + right_count

        return count_leaves(0)

    elif hasattr(tree_obj, "tree") and isinstance(tree_obj.tree, dict):
        # repo DT-CTS model with dict tree
        def count_leaves_dict(node):
            if "class" in node:
                return 1
            left_count = count_leaves_dict(node.get("left", {}))
            right_count = count_leaves_dict(node.get("right", {}))
            return left_count + right_count

        return count_leaves_dict(tree_obj.tree)

    else:
        return -1  # Unknown format


def compute_training_time_summary(training_times: Dict[str, float]) -> pd.DataFrame:
    """
    Format training times into a DataFrame.

    Args:
        training_times: Dict mapping model_name -> time_seconds

    Returns:
        DataFrame with model names and training times
    """
    rows = []
    for model_name, time_sec in training_times.items():
        rows.append({
            "model": model_name,
            "training_time_sec": time_sec,
        })
    return pd.DataFrame(rows)


def aggregate_benchmark_metrics(
    models_dict: Dict[str, object],
    X_test: np.ndarray,
    y_test: np.ndarray,
    y_pred_dict: Dict[str, np.ndarray],
    training_times: Dict[str, float],
) -> pd.DataFrame:
    """
    Aggregate all benchmark metrics into a single DataFrame.

    Args:
        models_dict: Dict mapping model_name -> trained_model
        X_test: Test features
        y_test: True test labels
        y_pred_dict: Dict mapping model_name -> predictions
        training_times: Dict mapping model_name -> training_time_sec

    Returns:
        DataFrame with all benchmark metrics
    """
    benchmark_rows = []

    for model_name in models_dict.keys():
        model = models_dict[model_name]
        y_pred = y_pred_dict[model_name]

        # Latency
        latency_metrics = measure_inference_latency(model, X_test)

        # FPR/FNR
        false_rate_metrics = measure_false_rates(y_test, y_pred)

        # Number of rules
        n_rules = count_decision_tree_rules(model)

        # Training time
        train_time = training_times.get(model_name, 0.0)

        row = {
            "model": model_name,
            "mean_latency_ms": latency_metrics["mean_latency_ms"],
            "p95_latency_ms": latency_metrics["p95_latency_ms"],
            "p99_latency_ms": latency_metrics["p99_latency_ms"],
            "fpr": false_rate_metrics["fpr"],
            "fnr": false_rate_metrics["fnr"],
            "tpr": false_rate_metrics["tpr"],
            "tnr": false_rate_metrics["tnr"],
            "tp": false_rate_metrics["tp"],
            "tn": false_rate_metrics["tn"],
            "fp": false_rate_metrics["fp"],
            "fn": false_rate_metrics["fn"],
            "n_rules": n_rules,
            "training_time_sec": train_time,
        }
        benchmark_rows.append(row)

    return pd.DataFrame(benchmark_rows)
