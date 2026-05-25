"""
Single-file benchmark for the CICIDS2017 hold-out split using 3/5/7 features and 3 models:
- DT
- RF
- DT-CTS

Outputs:
- reproduction/output/benchmark_cicids2017_dt_rf_dtcts.csv
- reproduction/output/benchmark_cicids2017_dt_rf_dtcts.png
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, precision_recall_fscore_support, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from config import MODEL_SCALE_MEDIUM, PAPER_FEATURE_CANDIDATES, RANDOM_STATE, TEST_SIZE
from data_pipeline import extract_cicids2017_zip, load_cicids2017_from_csv
from paper_features import (
    sanitize_feature_matrix,
    select_top_paper_features,
    available_paper_features,
)


plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans"],
        "font.size": 12,
        "axes.titlesize": 18,
        "axes.titleweight": "bold",
        "axes.labelsize": 14,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 13,
        "axes.linewidth": 1.0,
    }
)


REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "output"
DATASET_ZIP = REPO_ROOT / "datasets" / "CICIDS2017 .zip"
DATASET_COMBINE = REPO_ROOT / "datasets" / "combine.csv"
DT_CTS_FILE = REPO_ROOT.parent / "SISTAR" / "model" / "DT-CTS.py"

# Backward-compatible name used by generate_and_benchmark.py.
FEATURE_ORDER_7 = PAPER_FEATURE_CANDIDATES

CSV_TO_CANONICAL = {
    "Flow Packets/s": "flow_packets_persecond",
    "Packet Length Mean": "packet_length_mean",
    "Protocol": "protocol",
    "Init_Win_bytes_forward": "init_win_bytes_forward",
    "Fwd Header Length": "fwd_header_length",
    "Max Packet Length": "packet_length_max",
    "Min Packet Length": "packet_length_min",
    "Label": "raw_label",
}


def load_dt_cts_class():
    spec = importlib.util.spec_from_file_location("sistar_dt_cts", DT_CTS_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load DT-CTS from {DT_CTS_FILE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.DecisionTreeClassifier


def make_medium_models():
    DTCTS = load_dt_cts_class()
    return {
        "DT": DecisionTreeClassifier(
            max_depth=MODEL_SCALE_MEDIUM["max_depth"],
            min_samples_split=MODEL_SCALE_MEDIUM["min_samples_split"],
            ccp_alpha=MODEL_SCALE_MEDIUM["dt_ccp_alpha"],
            random_state=RANDOM_STATE,
        ),
        "RF": RandomForestClassifier(
            n_estimators=MODEL_SCALE_MEDIUM["n_estimators"],
            max_depth=MODEL_SCALE_MEDIUM["max_depth"],
            min_samples_split=MODEL_SCALE_MEDIUM["min_samples_split"],
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "DT-CTS": DTCTS(
            max_depth=MODEL_SCALE_MEDIUM["max_depth"],
            min_samples_split=MODEL_SCALE_MEDIUM["min_samples_split"],
            max_candidate_thresholds=MODEL_SCALE_MEDIUM["dtcts_max_candidate_thresholds"],
            max_thresholds_per_feature=MODEL_SCALE_MEDIUM["dtcts_max_thresholds_per_feature"],
        ),
    }


def _count_dt_thresholds(model) -> int:
    return int(np.count_nonzero(model.tree_.feature >= 0))


def _count_rf_thresholds(model) -> int:
    return int(sum(np.count_nonzero(estimator.tree_.feature >= 0) for estimator in model.estimators_))


def _count_dtcts_thresholds(model) -> int:
    acc = {}

    def walk(node):
        if not node or "class" in node:
            return
        acc.setdefault(int(node["feature"]), set()).add(float(node["threshold"]))
        walk(node.get("left"))
        walk(node.get("right"))

    walk(model.tree)
    return int(sum(len(v) for v in acc.values()))


def load_cicids2017_from_combine() -> pd.DataFrame:
    if DATASET_COMBINE.exists():
        sampled = load_cicids2017_from_csv(DATASET_COMBINE)
        benign_count = int((sampled["label"] == 0).sum())
        attack_count = int((sampled["label"] == 1).sum())
        if benign_count == 0 or attack_count == 0:
            raise ValueError("Need both benign and attack rows")

        sampled = sampled.sample(frac=1.0, random_state=42).reset_index(drop=True)

        needed = available_paper_features(sampled)
        for f in needed:
            upper = sampled[f].quantile(0.999)
            sampled[f] = sampled[f].clip(lower=0, upper=upper)

        return sampled

    extracted_csv = extract_cicids2017_zip(DATASET_ZIP)
    sampled = load_cicids2017_from_csv(extracted_csv)

    benign_count = int((sampled["label"] == 0).sum())
    attack_count = int((sampled["label"] == 1).sum())
    if benign_count == 0 or attack_count == 0:
        raise ValueError("Need both benign and attack rows")

    sampled = sampled.sample(frac=1.0, random_state=42).reset_index(drop=True)

    needed = available_paper_features(sampled)
    for f in needed:
        upper = sampled[f].quantile(0.999)
        sampled[f] = sampled[f].clip(lower=0, upper=upper)

    return sampled


def benchmark(df: pd.DataFrame) -> pd.DataFrame:
    feature_counts = [3, 5, 7]

    rows: List[Dict] = []
    train_df, test_df = train_test_split(
        df,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=df["label"],
    )
    selected_order = select_top_paper_features(train_df, max_features=max(feature_counts))

    for n_feat in feature_counts:
        selected = selected_order[: min(n_feat, len(selected_order))]
        if len(selected) < 3:
            raise ValueError("Not enough features in dataset to run 3/5/7 benchmark")

        X_train, caps = sanitize_feature_matrix(train_df, selected)
        X_test, _ = sanitize_feature_matrix(test_df, selected, caps=caps)
        y_train = train_df["label"].to_numpy(dtype=int)
        y_test = test_df["label"].to_numpy(dtype=int)

        models = make_medium_models()

        for name, model in models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            precision_attack, recall_attack, f1_attack, support_attack = precision_recall_fscore_support(
                y_test, y_pred, labels=[1], zero_division=0
            )

            # Confusion matrix counts (TN, FP, FN, TP)
            cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
            if cm.size == 4:
                tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])
            else:
                flat = cm.flatten()
                tn = int(flat[0]) if flat.size > 0 else 0
                fp = int(flat[1]) if flat.size > 1 else 0
                fn = int(flat[2]) if flat.size > 2 else 0
                tp = int(flat[3]) if flat.size > 3 else 0

            # Save a small confusion-matrix image for this run
            cm_dir = OUTPUT_DIR / "confusion_matrices"
            cm_dir.mkdir(parents=True, exist_ok=True)
            cm_fig, cm_ax = plt.subplots(figsize=(3.4, 3.4))
            cm_im = cm_ax.imshow(cm, interpolation='nearest', cmap="Blues")
            for (i, j), val in np.ndenumerate(cm):
                cm_ax.text(j, i, int(val), ha='center', va='center', color='black', fontsize=10)
            cm_ax.set_xticks([0, 1])
            cm_ax.set_yticks([0, 1])
            cm_ax.set_xticklabels(["Pred: Benign(0)", "Pred: Attack(1)"], fontsize=8)
            cm_ax.set_yticklabels(["True: Benign(0)", "True: Attack(1)"], fontsize=8)
            cm_ax.set_ylabel("Actual")
            cm_ax.set_xlabel("Predicted")
            cm_ax.set_title(f"CM: {name} ({n_feat} features)")
            cm_fig.tight_layout()
            cm_path = cm_dir / f"confusion_{name}_f{n_feat}.png"
            cm_fig.savefig(cm_path, dpi=140)
            plt.close(cm_fig)
            if name == "DT":
                threshold_count = _count_dt_thresholds(model)
            elif name == "RF":
                threshold_count = _count_rf_thresholds(model)
            else:
                threshold_count = _count_dtcts_thresholds(model)

            rows.append(
                {
                    "feature_count": n_feat,
                    "model_scale": "medium",
                    "features_used": ",".join(selected),
                    "model": name,
                    "accuracy": float(accuracy_score(y_test, y_pred)),
                    "f1": float(f1_score(y_test, y_pred)),
                    "balanced_accuracy": float(balanced_accuracy_score(y_test, y_pred)),
                    "f1_macro": float(f1_score(y_test, y_pred, average="macro")),
                    "precision_attack": float(precision_attack[0]),
                    "recall_attack": float(recall_attack[0]),
                    "f1_attack": float(f1_attack[0]),
                    "support_attack": int(support_attack[0]),
                    "threshold_count": int(threshold_count),
                    "tn": tn,
                    "fp": fp,
                    "fn": fn,
                    "tp": tp,
                    "confusion_png": str(cm_path),
                }
            )

    results_df = pd.DataFrame(rows)
    dt_thresholds = (
        results_df[results_df["model"] == "DT"]
        .set_index("feature_count")["threshold_count"]
        .to_dict()
    )
    results_df["threshold_reduction_vs_dt_pct"] = results_df.apply(
        lambda row: 100.0
        * (dt_thresholds.get(row["feature_count"], row["threshold_count"]) - row["threshold_count"])
        / max(dt_thresholds.get(row["feature_count"], row["threshold_count"]), 1),
        axis=1,
    )
    results_df["f1_per_threshold"] = results_df.apply(
        lambda row: row["f1"] / max(row["threshold_count"], 1),
        axis=1,
    )

    return results_df


def save_plot(results_df: pd.DataFrame) -> Path:
    models = ["DT", "RF", "DT-CTS"]
    feature_counts = [3, 5, 7]
    colors = {"DT": "#4C78A8", "RF": "#F58518", "DT-CTS": "#54A24B"}

    metrics = [
        ("accuracy", "Accuracy"),
        ("balanced_accuracy", "Balanced Accuracy"),
        ("precision_attack", "Precision (Attack Class)"),
        ("recall_attack", "Recall (Attack Class)"),
        ("threshold_count", "Threshold Count"),
    ]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_paths = []

    x = np.arange(len(feature_counts))
    width = 0.25

    for col, title in metrics:
        fig, ax = plt.subplots(figsize=(12, 8))
        for i, model in enumerate(models):
            vals = []
            for fc in feature_counts:
                row = results_df[(results_df["feature_count"] == fc) & (results_df["model"] == model)]
                vals.append(float(row.iloc[0][col]) if not row.empty else 0.0)
            offset = (i - 1) * width
            bars = ax.bar(x + offset, vals, width=width, label=model, color=colors[model])
            fmt = "%.3f" if col != "threshold_count" else "%.0f"
            ax.bar_label(bars, fmt=fmt, padding=3, fontsize=10)

        ax.set_title(title, pad=10)
        ax.set_xticks(x)
        ax.set_xticklabels(feature_counts)
        ax.set_xlabel("Number of Features")
        ax.set_ylabel("Score / Count")
        ax.grid(axis="y", linestyle="--", alpha=0.45)
        ax.tick_params(axis="both", which="major", labelsize=12)

        if col == "threshold_count":
            max_value = max(float(results_df[col].max()), 1.0)
            ax.set_ylim(0, max_value * 1.18)
        else:
            ax.set_ylim(0, 1.05)

        handles, labels = ax.get_legend_handles_labels()
        fig.legend(handles, labels, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 0.98), frameon=True)
        fig.tight_layout(rect=[0, 0, 1, 0.92])

        out_png = OUTPUT_DIR / f"benchmark_{col}.png"
        fig.savefig(out_png, dpi=160, bbox_inches="tight")
        plt.close(fig)
        out_paths.append(out_png)

    # Return first metric path for backward compatibility
    return out_paths[0]


def save_f1_plot(results_df: pd.DataFrame) -> Path:
    models = ["DT", "RF", "DT-CTS"]
    feature_counts = [3, 5, 7]
    colors = {"DT": "#4C78A8", "RF": "#F58518", "DT-CTS": "#54A24B"}

    fig, ax = plt.subplots(figsize=(12, 8))
    x = np.arange(len(feature_counts))
    width = 0.25

    for i, model in enumerate(models):
        vals = []
        for fc in feature_counts:
            row = results_df[(results_df["feature_count"] == fc) & (results_df["model"] == model)]
            vals.append(float(row.iloc[0]["f1"]) if not row.empty else 0.0)
        offset = (i - 1) * width
        bars = ax.bar(x + offset, vals, width=width, label=model, color=colors[model])
        ax.bar_label(bars, fmt="%.3f", padding=3, fontsize=10)

    ax.set_title("F1 Score by Model and Number of Features", pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(feature_counts)
    ax.set_xlabel("Number of Features")
    ax.set_ylabel("F1 Score")
    ax.set_ylim(0, 1.05)
    ax.grid(axis="y", linestyle="--", alpha=0.45)
    ax.tick_params(axis="both", which="major", labelsize=12)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 0.98), frameon=True)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_png = OUTPUT_DIR / "benchmark_f1_scores.png"
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(out_png, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return out_png


def save_accept_deny_plot(results_df: pd.DataFrame) -> List[Path]:
    feature_counts = [3, 5, 7]
    models = ["DT", "RF", "DT-CTS"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_paths: List[Path] = []

    for fc in feature_counts:
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        for ci, cls in enumerate(["Benign", "Attack"]):
            ax = axes[ci]
            accepted = []
            denied = []
            for model in models:
                row = results_df[(results_df["feature_count"] == fc) & (results_df["model"] == model)]
                if row.empty:
                    tn = fp = fn = tp = 0
                else:
                    tn = int(row.iloc[0].get("tn", 0))
                    fp = int(row.iloc[0].get("fp", 0))
                    fn = int(row.iloc[0].get("fn", 0))
                    tp = int(row.iloc[0].get("tp", 0))

                if cls == "Benign":
                    accepted.append(tn)
                    denied.append(fp)
                else:
                    accepted.append(fn)  # attack accepted = false negatives
                    denied.append(tp)   # attack denied = true positives

            x = np.arange(len(models))
            width = 0.35
            p1 = ax.bar(x - width / 2, accepted, width=width, label="Accepted", color="#6BAED6")
            p2 = ax.bar(x + width / 2, denied, width=width, label="Denied", color="#FD8D3C")
            ax.set_xticks(x)
            ax.set_xticklabels(models)
            ax.set_title(f"{cls} flows (features={fc})", pad=10)
            ax.set_ylabel("Count")
            ax.tick_params(axis="both", which="major", labelsize=12)

            max_value = max(accepted + denied + [1])
            ax.set_ylim(0, max_value * 1.15)

        # place legend above the figure
        handles = [p1, p2]
        labels = [h.get_label() for h in handles]
        fig.legend(handles, labels, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 0.98), frameon=True)
        fig.tight_layout(rect=[0, 0, 1, 0.92])
        out_png = OUTPUT_DIR / f"benchmark_accept_deny_f{fc}.png"
        fig.savefig(out_png, dpi=160, bbox_inches="tight")
        plt.close(fig)
        out_paths.append(out_png)

    return out_paths


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_cicids2017_from_combine()
    results_df = benchmark(df)

    out_csv = OUTPUT_DIR / "benchmark_cicids2017_dt_rf_dtcts.csv"
    results_df.to_csv(out_csv, index=False)

    out_png = save_plot(results_df)
    out_f1 = save_f1_plot(results_df)
    out_accept_deny_list = save_accept_deny_plot(results_df)

    print("[OK] Dataset:", DATASET_ZIP)
    print("[OK] Saved CSV:", out_csv)
    print("[OK] Saved plot:", out_png)
    print("[OK] Saved F1 plot:", out_f1)
    for p in out_accept_deny_list:
        print("[OK] Saved accept/deny plot:", p)
    print("\nResults:")
    print(results_df.to_string(index=False))


if __name__ == "__main__":
    main()
