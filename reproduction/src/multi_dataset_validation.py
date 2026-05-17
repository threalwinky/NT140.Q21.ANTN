"""
Multi-Dataset Validation: Test DT-CTS generalization across different DDoS attack types.

This script trains and evaluates DT-CTS on multiple datasets to verify the model's
generalization capability across different attack scenarios (SYN Flood, UDP Flood,
HTTP Flood, etc.).

Datasets:
1. CICIDS2017 (DoS-Wednesday)
2. CICIDS2018 (synthetic variant - DDoS-Tuesday)
3. CIC-DDoS2019 (synthetic variant - high-intensity)
4. CICIoT2023 (synthetic variant - IoT botnet)
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

OUTPUT = Path(__file__).parent.parent / "output"


def load_repo_dt_cts():
    """Load DT-CTS model from SISTAR repository."""
    spec = importlib.util.spec_from_file_location("sistar_dt_cts", SISTAR_MODEL)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {SISTAR_MODEL}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.DecisionTreeClassifier


def generate_dataset_variant(
    dataset_name: str,
    n_benign: int = 2400,
    n_attack: int = 2400,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate synthetic dataset variant for different attack scenarios.

    Args:
        dataset_name: One of ['CICIDS2017', 'CICIDS2018', 'CIC-DDoS2019', 'CICIoT2023']
        n_benign: Number of benign flows
        n_attack: Number of attack flows
        seed: Random seed for reproducibility

    Returns:
        DataFrame with features and labels
    """
    rng = np.random.default_rng(seed)

    # Benign traffic - common baseline
    benign_protocol = rng.choice([6, 17], size=n_benign, p=[0.8, 0.2])
    benign_win = np.clip(rng.normal(22000, 9000, n_benign), 1024, 65535)
    benign_hdr = np.clip(rng.normal(420, 120, n_benign), 60, 1600)
    benign_pkt_mean = np.clip(rng.normal(820, 220, n_benign), 64, 1500)
    benign_pps = np.clip(rng.normal(180, 85, n_benign), 5, 700)

    benign = pd.DataFrame(
        {
            "protocol": benign_protocol.astype(int),
            "init_win_bytes_forward": benign_win.astype(float),
            "fwd_header_length": benign_hdr.astype(float),
            "packet_length_mean": benign_pkt_mean.astype(float),
            "flow_packets_persecond": benign_pps.astype(float),
            "label": 0,
            "attack_type": "benign",
        }
    )

    # Attack traffic - varies by dataset
    if dataset_name == "CICIDS2017":
        # DoS attacks: Hulk, Slowloris, GoldenEye - moderate intensity
        attack_kind = rng.choice(["hulk", "slowloris", "golden"], size=n_attack, p=[0.4, 0.3, 0.3])
        intensity_multiplier = 1.0

    elif dataset_name == "CICIDS2018":
        # DDoS attacks: HTTP Flood, LOIC - medium intensity, mixed protocols
        attack_kind = rng.choice(["http_flood", "loic", "syn"], size=n_attack, p=[0.4, 0.35, 0.25])
        intensity_multiplier = 1.2

    elif dataset_name == "CIC-DDoS2019":
        # High-intensity: SYN Flood, UDP Flood, ICMP Flood, DNS amplification
        attack_kind = rng.choice(
            ["syn_flood", "udp_flood", "icmp_flood", "dns_amp"],
            size=n_attack,
            p=[0.3, 0.25, 0.25, 0.2],
        )
        intensity_multiplier = 1.8  # Higher intensity attacks

    elif dataset_name == "CICIoT2023":
        # IoT botnet DDoS: Mirai variants, distributed
        attack_kind = rng.choice(["mirai_syn", "mirai_udp", "mirai_http"], size=n_attack, p=[0.4, 0.35, 0.25])
        intensity_multiplier = 1.5  # Moderate-high, distributed

    else:
        raise ValueError(f"Unknown dataset_name: {dataset_name}")

    # Generate attack traffic with varying characteristics
    attack_protocol = np.empty(n_attack)
    attack_win = np.empty(n_attack)
    attack_hdr = np.empty(n_attack)
    attack_pkt_mean = np.empty(n_attack)
    attack_pps = np.empty(n_attack)

    for i, kind in enumerate(attack_kind):
        if kind in ["hulk", "syn_flood", "mirai_syn"]:
            # SYN-like attacks: small window, high packet rate
            attack_protocol[i] = 6
            attack_win[i] = np.clip(rng.normal(256, 128, 1)[0], 0, 4096)
            attack_hdr[i] = np.clip(rng.normal(72, 18, 1)[0], 40, 180)
            attack_pkt_mean[i] = np.clip(rng.normal(88, 25, 1)[0], 40, 250)
            attack_pps[i] = np.clip(rng.normal(1500 * intensity_multiplier, 320, 1)[0], 250, 4000)

        elif kind in ["udp_flood", "loic", "mirai_udp"]:
            # UDP-like attacks: UDP protocol, moderate window, high rate
            attack_protocol[i] = 17
            attack_win[i] = np.clip(rng.normal(2048, 1024, 1)[0], 0, 8192)
            attack_hdr[i] = np.clip(rng.normal(110, 35, 1)[0], 40, 400)
            attack_pkt_mean[i] = np.clip(rng.normal(180, 50, 1)[0], 60, 400)
            attack_pps[i] = np.clip(rng.normal(1250 * intensity_multiplier, 280, 1)[0], 250, 3500)

        elif kind in ["http_flood", "mirai_http"]:
            # HTTP-like attacks: TCP, larger packets, application-level
            attack_protocol[i] = 6
            attack_win[i] = np.clip(rng.normal(512, 256, 1)[0], 0, 4096)
            attack_hdr[i] = np.clip(rng.normal(150, 40, 1)[0], 60, 500)
            attack_pkt_mean[i] = np.clip(rng.normal(320, 80, 1)[0], 80, 700)
            attack_pps[i] = np.clip(rng.normal(900 * intensity_multiplier, 200, 1)[0], 150, 2500)

        elif kind in ["slowloris", "golden"]:
            # Slowloris/GoldenEye: persistent, lower rate, longer duration
            attack_protocol[i] = 6
            attack_win[i] = np.clip(rng.normal(512, 200, 1)[0], 0, 4096)
            attack_hdr[i] = np.clip(rng.normal(140, 35, 1)[0], 60, 450)
            attack_pkt_mean[i] = np.clip(rng.normal(280, 70, 1)[0], 80, 600)
            attack_pps[i] = np.clip(rng.normal(450 * intensity_multiplier, 150, 1)[0], 100, 1500)

        elif kind in ["icmp_flood", "dns_amp"]:
            # ICMP/DNS: high volume, small packets
            attack_protocol[i] = 17 if kind == "dns_amp" else 1
            attack_win[i] = np.clip(rng.normal(2048, 1024, 1)[0], 0, 8192)
            attack_hdr[i] = np.clip(rng.normal(85, 25, 1)[0], 40, 300)
            attack_pkt_mean[i] = np.clip(rng.normal(120, 40, 1)[0], 40, 300)
            attack_pps[i] = np.clip(rng.normal(2000 * intensity_multiplier, 400, 1)[0], 500, 6000)

    attack = pd.DataFrame(
        {
            "protocol": attack_protocol.astype(int),
            "init_win_bytes_forward": attack_win.astype(float),
            "fwd_header_length": attack_hdr.astype(float),
            "packet_length_mean": attack_pkt_mean.astype(float),
            "flow_packets_persecond": attack_pps.astype(float),
            "label": 1,
            "attack_type": attack_kind,
        }
    )

    df = pd.concat([benign, attack], ignore_index=True)
    return df.sample(frac=1.0, random_state=seed).reset_index(drop=True)


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
    """Run multi-dataset validation across different attack scenarios."""
    print("\n" + "=" * 70)
    print("🌍 MULTI-DATASET VALIDATION: DT-CTS Generalization Test")
    print("=" * 70)

    datasets = [
        "CICIDS2017",
        "CICIDS2018",
        "CIC-DDoS2019",
        "CICIoT2023",
    ]

    results = []

    # Process each dataset
    for dataset_name in datasets:
        # Try to load real dataset, fall back to synthetic
        if dataset_name == "CICIDS2017":
            try:
                df, source = pd.read_csv(OUTPUT / "dataset_used.csv"), "Real Kaggle CICIDS2017 (if available)"
                if len(df) == 0:
                    raise ValueError("Empty dataset")
            except Exception:
                df = generate_dataset_variant(dataset_name, n_benign=2400, n_attack=2400, seed=42)
                source = "Synthetic variant (DoS attacks)"
        else:
            df = generate_dataset_variant(dataset_name, n_benign=2400, n_attack=2400, seed=42)
            source = f"Synthetic variant ({dataset_name} attack profile)"

        metrics = train_and_evaluate_dataset(dataset_name, df)
        metrics["source"] = source
        results.append(metrics)

    # Create results DataFrame
    results_df = pd.DataFrame(results)

    # Save results
    results_df.to_csv(OUTPUT / "multi_dataset_validation.csv", index=False)
    print(f"\n✅ Results saved to: multi_dataset_validation.csv")

    # Print summary table
    print("\n" + "=" * 70)
    print("📊 SUMMARY: Multi-Dataset Validation Results")
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

    print(f"\n📈 Cross-Dataset Performance:")
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

    print(f"\n✅ DT-CTS shows {'GOOD' if std_accuracy < 0.02 else 'MODERATE' if std_accuracy < 0.05 else 'VARIABLE'} generalization")
    print(f"   across different attack types and datasets.")

    print("\n" + "=" * 70 + "\n")

    return results_df


if __name__ == "__main__":
    run_multi_dataset_validation()
