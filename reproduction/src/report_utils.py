from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from config import FEATURE_NAMES, OUTPUT

MODEL_COLORS = {
    "DT": "#4C78A8",
    "RF": "#F58518",
    "DT-CTS": "#54A24B",
}

POLICY_COLORS = {
    "no_pushback": "#9D755D",
    "immediate_pushback": "#E45756",
    "gated_pushback": "#72B7B2",
}

FEATURE_COLORS = {
    "protocol": "#4C78A8",
    "init_win_bytes_forward": "#F58518",
    "fwd_header_length": "#E45756",
    "packet_length_mean": "#72B7B2",
    "flow_packets_persecond": "#54A24B",
}


def _model_colors(names):
    return [MODEL_COLORS.get(name, "#4C78A8") for name in names]


def _policy_colors(names):
    return [POLICY_COLORS.get(name, "#9D755D") for name in names]


def _display_feature_name(name: str) -> str:
    return name.replace("_", "\n")


def _apply_axis_style(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    ax.set_axisbelow(True)


def save_bar_plot(metrics_df: pd.DataFrame, column: str, out_path: Path, title: str):
    fig, ax = plt.subplots(figsize=(7, 4))
    names = metrics_df["model"].tolist()
    ax.bar(names, metrics_df[column].tolist(), color=_model_colors(names))
    ax.set_ylim(0, 1 if column != "total_thresholds" else max(metrics_df[column].tolist()) * 1.15)
    ax.set_title(title)
    ax.set_ylabel(column.replace("_", " ").title())
    _apply_axis_style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def save_threshold_plot(threshold_df: pd.DataFrame, out_path: Path):
    fig, ax = plt.subplots(figsize=(7, 4))
    names = threshold_df["model"].tolist()
    ax.bar(names, threshold_df["total_thresholds"], color=_model_colors(names))
    ax.set_ylabel("Total thresholds")
    ax.set_title("Threshold usage comparison")
    _apply_axis_style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def save_pushback_plot(pushback_detail: pd.DataFrame, out_path: Path):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for policy in ["no_pushback", "immediate_pushback", "gated_pushback"]:
        subset = (
            pushback_detail[pushback_detail["policy"] == policy]
            .groupby("window", as_index=False)["attack_bytes_reaching_victim"]
            .sum()
        )
        ax.plot(
            subset["window"],
            subset["attack_bytes_reaching_victim"],
            label=policy,
            color=POLICY_COLORS.get(policy, "#9D755D"),
            linewidth=2,
        )
    ax.set_title("Attack bytes reaching victim by policy")
    ax.set_xlabel("Time window")
    ax.set_ylabel("Attack bytes")
    ax.legend()
    _apply_axis_style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def save_metric_suite(metrics_df: pd.DataFrame, out_path: Path):
    metrics = ["accuracy", "precision", "recall", "f1"]
    metric_labels = ["Accuracy", "Precision", "Recall", "F1"]
    models = metrics_df["model"].tolist()
    width = 0.22
    x_positions = list(range(len(metrics)))

    fig, ax = plt.subplots(figsize=(9, 4.8))
    for idx, model in enumerate(models):
        values = [
            float(metrics_df.loc[metrics_df["model"] == model, metric].iloc[0])
            for metric in metrics
        ]
        shifted = [x + (idx - 1) * width for x in x_positions]
        ax.bar(shifted, values, width=width, label=model, color=MODEL_COLORS.get(model, "#4C78A8"))

    ax.set_xticks(x_positions)
    ax.set_xticklabels(metric_labels)
    ax.set_ylim(0.85, 1.0)
    ax.set_ylabel("Score")
    ax.set_title("Model quality comparison")
    ax.legend()
    _apply_axis_style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def save_threshold_feature_plot(threshold_df: pd.DataFrame, out_path: Path):
    models = threshold_df["model"].tolist()
    threshold_maps = {
        row["model"]: json.loads(row["thresholds_per_feature"])
        for _, row in threshold_df.iterrows()
    }

    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    bottoms = [0] * len(models)
    for feature in FEATURE_NAMES:
        values = [threshold_maps.get(model, {}).get(feature, 0) for model in models]
        ax.bar(
            models,
            values,
            bottom=bottoms,
            label=_display_feature_name(feature),
            color=FEATURE_COLORS.get(feature, "#4C78A8"),
        )
        bottoms = [bottom + value for bottom, value in zip(bottoms, values)]

    ax.set_ylabel("Threshold count")
    ax.set_title("Thresholds grouped by feature")
    ax.legend(loc="upper right", fontsize=8)
    _apply_axis_style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def save_pushback_summary_plot(pushback_df: pd.DataFrame, out_path: Path):
    policies = pushback_df["policy"].tolist()
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
    columns = [
        ("attack_bytes_reaching_victim", "Attack bytes to victim"),
        ("benign_bytes_reaching_victim", "Benign bytes preserved"),
        ("false_block_events", "False block events"),
    ]

    for ax, (column, title) in zip(axes, columns):
        ax.bar(policies, pushback_df[column], color=_policy_colors(policies))
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=12)
        _apply_axis_style(ax)
        if "bytes" in column:
            ax.ticklabel_format(style="plain", axis="y")

    fig.suptitle("Pushback policy comparison", fontsize=13)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def save_reproduction_dashboard(
    metrics_df: pd.DataFrame,
    threshold_df: pd.DataFrame,
    pushback_df: pd.DataFrame,
    out_path: Path,
):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    metric_models = metrics_df["model"].tolist()
    axes[0, 0].bar(metric_models, metrics_df["f1"], color=_model_colors(metric_models))
    axes[0, 0].set_ylim(0.85, 1.0)
    axes[0, 0].set_title("F1 by model")
    axes[0, 0].set_ylabel("F1")
    _apply_axis_style(axes[0, 0])

    threshold_models = threshold_df["model"].tolist()
    axes[0, 1].bar(
        threshold_models,
        threshold_df["total_thresholds"],
        color=_model_colors(threshold_models),
    )
    axes[0, 1].set_title("Total thresholds")
    axes[0, 1].set_ylabel("Count")
    _apply_axis_style(axes[0, 1])

    policies = pushback_df["policy"].tolist()
    axes[1, 0].bar(
        policies,
        pushback_df["attack_bytes_reaching_victim"],
        color=_policy_colors(policies),
    )
    axes[1, 0].set_title("Attack bytes reaching victim")
    axes[1, 0].tick_params(axis="x", rotation=12)
    axes[1, 0].ticklabel_format(style="plain", axis="y")
    _apply_axis_style(axes[1, 0])

    axes[1, 1].bar(
        policies,
        pushback_df["benign_bytes_reaching_victim"],
        color=_policy_colors(policies),
    )
    axes[1, 1].set_title("Benign bytes preserved")
    axes[1, 1].tick_params(axis="x", rotation=12)
    axes[1, 1].ticklabel_format(style="plain", axis="y")
    _apply_axis_style(axes[1, 1])

    fig.suptitle("Reduced SISTAR reproduction dashboard", fontsize=14)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


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
