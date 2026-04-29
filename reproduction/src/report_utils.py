from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from config import OUTPUT


def save_bar_plot(metrics_df: pd.DataFrame, column: str, out_path: Path, title: str):
    plt.figure(figsize=(7, 4))
    plt.bar(metrics_df["model"].tolist(), metrics_df[column].tolist())
    plt.ylim(0, 1 if column != "total_thresholds" else max(metrics_df[column].tolist()) * 1.15)
    plt.title(title)
    plt.ylabel(column.replace("_", " ").title())
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def save_threshold_plot(threshold_df: pd.DataFrame, out_path: Path):
    plt.figure(figsize=(7, 4))
    plt.bar(threshold_df["model"], threshold_df["total_thresholds"])
    plt.ylabel("Total thresholds")
    plt.title("Threshold usage comparison")
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def save_pushback_plot(pushback_detail: pd.DataFrame, out_path: Path):
    plt.figure(figsize=(8, 4.5))
    for policy in ["no_pushback", "immediate_pushback", "gated_pushback"]:
        subset = (
            pushback_detail[pushback_detail["policy"] == policy]
            .groupby("window", as_index=False)["attack_bytes_reaching_victim"]
            .sum()
        )
        plt.plot(subset["window"], subset["attack_bytes_reaching_victim"], label=policy)
    plt.title("Attack bytes reaching victim by policy")
    plt.xlabel("Time window")
    plt.ylabel("Attack bytes")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def write_summary(metrics_df: pd.DataFrame, threshold_df: pd.DataFrame, pushback_df: pd.DataFrame):
    best_f1_row = metrics_df.sort_values("f1", ascending=False).iloc[0]
    dt_thresholds = int(threshold_df.loc[threshold_df["model"] == "DT", "total_thresholds"].iloc[0])
    dt_cts_thresholds = int(threshold_df.loc[threshold_df["model"] == "DT-CTS", "total_thresholds"].iloc[0])
    reduction = 100.0 * (dt_thresholds - dt_cts_thresholds) / max(dt_thresholds, 1)

    no_push = pushback_df.loc[pushback_df["policy"] == "no_pushback"].iloc[0]
    gated = pushback_df.loc[pushback_df["policy"] == "gated_pushback"].iloc[0]
    attack_reduction = 100.0 * (
        no_push["attack_bytes_reaching_victim"] - gated["attack_bytes_reaching_victim"]
    ) / max(no_push["attack_bytes_reaching_victim"], 1)

    dataset_source = (OUTPUT / "dataset_source.txt").read_text(encoding="utf-8").strip()
    lines = [
        "# Reduced SISTAR reproduction summary",
        "",
        "## Dataset",
        f"- Source: `{dataset_source}`",
        "",
        "## Classification",
        f"- Best F1 in this reduced run: `{best_f1_row['model']}` with `{best_f1_row['f1']:.4f}`",
        f"- `DT-CTS` F1: `{metrics_df.loc[metrics_df['model'] == 'DT-CTS', 'f1'].iloc[0]:.4f}`",
        f"- `DT` F1: `{metrics_df.loc[metrics_df['model'] == 'DT', 'f1'].iloc[0]:.4f}`",
        f"- `RF` F1: `{metrics_df.loc[metrics_df['model'] == 'RF', 'f1'].iloc[0]:.4f}`",
        "",
        "## Threshold efficiency",
        f"- `DT` total thresholds: `{dt_thresholds}`",
        f"- `DT-CTS` total thresholds: `{dt_cts_thresholds}`",
        f"- Threshold reduction vs DT: `{reduction:.2f}%`",
        "",
        "## Pushback simulation",
        f"- Attack bytes reaching victim without pushback: `{no_push['attack_bytes_reaching_victim']:.0f}`",
        f"- Attack bytes reaching victim with gated pushback: `{gated['attack_bytes_reaching_victim']:.0f}`",
        f"- Attack-byte reduction from the small improvement: `{attack_reduction:.2f}%`",
        f"- Benign bytes preserved with gated pushback: `{gated['benign_bytes_reaching_victim']:.0f}`",
        f"- False block events with gated pushback: `{int(gated['false_block_events'])}`",
        "",
        "## Small improvement beyond the paper",
        "- This reduced reproduction adds `gated_pushback`: only trigger upstream blocking after two consecutive malicious detections.",
        "- Goal: preserve more benign traffic than naive immediate pushback while still reducing attack traffic strongly.",
    ]
    (OUTPUT / "summary.md").write_text("\n".join(lines), encoding="utf-8")
