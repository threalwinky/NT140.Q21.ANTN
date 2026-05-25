"""
Legacy benchmark helper for the current `combine.csv` + `data_benchmark.csv` workflow.

This module remains as a compatibility entrypoint, but the active demo now trains on
the full `combine.csv` dataset and evaluates the generated `data_benchmark.csv` file.
"""

from __future__ import annotations

import importlib.util
import time
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from benchmark_metrics import (
    aggregate_benchmark_metrics,
    count_decision_tree_rules,
    measure_false_rates,
    measure_inference_latency,
)
from config import FEATURE_NAMES, SISTAR_MODEL
from data_pipeline import build_dataset, synthesize_flows
from paper_benchmark_3models import load_cicids2017_from_combine

OUTPUT = Path(__file__).parent.parent / "output"


def load_repo_dt_cts():
    """Load DT-CTS model from SISTAR repository."""
    spec = importlib.util.spec_from_file_location("sistar_dt_cts", SISTAR_MODEL)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {SISTAR_MODEL}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.DecisionTreeClassifier


def generate_dataset_variant(*args, **kwargs) -> pd.DataFrame:
    """Compatibility shim.

    The current workflow no longer uses legacy synthetic dataset variants.
    """
    raise RuntimeError("Legacy dataset variants are not part of the current workflow")


def train_and_evaluate_dataset(
    dataset_name: str,
    df: pd.DataFrame,
) -> Dict[str, float | int | str]:
    """
    Train DT-CTS on a single dataset and compute metrics.

    Returns:
        Dictionary with metrics for this dataset
    """
    print(f"\n{'=' * 70}")
    print(f"🔄 Processing: {dataset_name}")
    print(f"{'=' * 70}")
    print(f"Dataset size: {len(df)} flows ({(df['label'] == 1).sum()} attacks, {(df['label'] == 0).sum()} benign)")

    X = df[FEATURE_NAMES].to_numpy(dtype=float)
    y = df["label"].to_numpy(dtype=int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    # Load and train DT-CTS
    RepoDTCTS = load_repo_dt_cts()
    model = RepoDTCTS(max_depth=6, min_samples_split=20)

    start_time = time.time()
    model.fit(X_train, y_train)
    training_time = time.time() - start_time

    y_pred = model.predict(X_test)

    # Compute metrics
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)

    # Benchmark metrics
    latency_info = measure_inference_latency(model, X_test, n_warmup=10)
    false_rates = measure_false_rates(y_test, y_pred)
    n_rules = count_decision_tree_rules(model)

    print(f"\n✅ Metrics for {dataset_name}:")
    print(f"   Accuracy: {accuracy:.4f} | F1: {f1:.4f} | Precision: {precision:.4f} | Recall: {recall:.4f}")
    print(f"   Latency: {latency_info['mean_latency_ms']:.6f} ms (mean)")
    print(f"   FPR: {false_rates['fpr']*100:.2f}% | FNR: {false_rates['fnr']*100:.2f}%")
    print(f"   Rules: {n_rules} | Training Time: {training_time:.4f}s")

    return {
        "dataset": dataset_name,
        "n_samples": len(df),
        "n_attacks": (df["label"] == 1).sum(),
        "n_benign": (df["label"] == 0).sum(),
        "accuracy": accuracy,
        "f1_score": f1,
        "precision": precision,
        "recall": recall,
        "mean_latency_ms": latency_info["mean_latency_ms"],
        "p95_latency_ms": latency_info["p95_latency_ms"],
        "p99_latency_ms": latency_info["p99_latency_ms"],
        "fpr": false_rates["fpr"],
        "fnr": false_rates["fnr"],
        "tpr": false_rates["tpr"],
        "tnr": false_rates["tnr"],
        "n_rules": n_rules,
        "training_time_sec": training_time,
    }


def run_multi_dataset_validation():
    """Run benchmark validation on the generated `data_benchmark.csv` file."""
    print("\n" + "=" * 70)
    print("🌍 BENCHMARK VALIDATION: DT-CTS on data_benchmark.csv")
    print("=" * 70)

    data_benchmark_path = OUTPUT / "data_benchmark.csv"
    if data_benchmark_path.exists():
        df = pd.read_csv(data_benchmark_path)
        source = "Generated data_benchmark.csv"
    else:
        df = load_cicids2017_from_combine()
        source = "combine.csv"

    metrics = train_and_evaluate_dataset("DATA_BENCHMARK", df)
    metrics["source"] = source
    results = [metrics]

    # Create results DataFrame
    results_df = pd.DataFrame(results)

    # Save results
    results_df.to_csv(OUTPUT / "multi_dataset_validation.csv", index=False)
    print(f"\n✅ Results saved to: multi_dataset_validation.csv")

    # Print summary table
    print("\n" + "=" * 70)
    print("📊 SUMMARY: Benchmark Validation Results")
    print("=" * 70)

    summary_cols = [
        "dataset",
        "accuracy",
        "f1_score",
        "fpr",
        "fnr",
        "mean_latency_ms",
        "n_rules",
        "training_time_sec",
    ]
    summary_df = results_df[summary_cols].copy()
    summary_df["fpr"] = (summary_df["fpr"] * 100).round(2).astype(str) + "%"
    summary_df["fnr"] = (summary_df["fnr"] * 100).round(2).astype(str) + "%"
    summary_df["accuracy"] = summary_df["accuracy"].round(4)
    summary_df["f1_score"] = summary_df["f1_score"].round(4)
    summary_df["mean_latency_ms"] = summary_df["mean_latency_ms"].round(6)
    summary_df["training_time_sec"] = summary_df["training_time_sec"].round(4)

    print(summary_df.to_string(index=False))

    # Print insights
    print("\n" + "=" * 70)
    print("🎯 KEY INSIGHTS")
    print("=" * 70)

    avg_accuracy = results_df["accuracy"].mean()
    avg_f1 = results_df["f1_score"].mean()
    avg_latency = results_df["mean_latency_ms"].mean()
    max_fpr = results_df["fpr"].max() * 100
    max_fnr = results_df["fnr"].max() * 100

    print(f"\n📈 Benchmark Performance:")
    print(f"   Average Accuracy: {avg_accuracy:.4f}")
    print(f"   Average F1-Score: {avg_f1:.4f}")
    print(f"   Average Latency: {avg_latency:.6f} ms")
    print(f"   Max FPR: {max_fpr:.2f}% | Max FNR: {max_fnr:.2f}%")

    std_accuracy = results_df["accuracy"].std()
    std_f1 = results_df["f1_score"].std()
    print(f"\n📊 Variance (σ):")
    print(f"   Accuracy σ: {std_accuracy:.6f} (lower = more stable)")
    print(f"   F1-Score σ: {std_f1:.6f}")

    best_dataset = results_df.loc[results_df["accuracy"].idxmax(), "dataset"]
    worst_dataset = results_df.loc[results_df["accuracy"].idxmin(), "dataset"]
    print(f"\n🏆 Best Performance: {best_dataset} ({results_df['accuracy'].max():.4f})")
    print(f"📉 Lowest Performance: {worst_dataset} ({results_df['accuracy'].min():.4f})")

    print(f"\n✅ DT-CTS benchmark variance is {'LOW' if std_accuracy < 0.02 else 'MODERATE' if std_accuracy < 0.05 else 'HIGH'}")
    print(f"   on the current generated benchmark set.")

    print("\n" + "=" * 70 + "\n")

    return results_df


if __name__ == "__main__":
    run_multi_dataset_validation()
