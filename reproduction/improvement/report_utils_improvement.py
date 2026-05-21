from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

POLICY_ORDER = ["no_pushback", "immediate_pushback", "gated_pushback"]
POLICY_LABELS = {
    "no_pushback": "No pushback",
    "immediate_pushback": "Original\nimmediate",
    "gated_pushback": "Improved\ngated",
}
POLICY_COLORS = {
    "no_pushback": "#9D755D",
    "immediate_pushback": "#E45756",
    "gated_pushback": "#54A24B",
}


def _ordered(df: pd.DataFrame) -> pd.DataFrame:
    order = {policy: idx for idx, policy in enumerate(POLICY_ORDER)}
    return df.assign(_order=df["policy"].map(order)).sort_values("_order").drop(columns="_order")


def _labels(df: pd.DataFrame) -> list[str]:
    return [POLICY_LABELS.get(policy, policy) for policy in df["policy"]]


def _colors(df: pd.DataFrame) -> list[str]:
    return [POLICY_COLORS.get(policy, "#4C78A8") for policy in df["policy"]]


def _apply_axis_style(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.25)
    ax.set_axisbelow(True)


def _annotate_bars(ax, values, percent: bool = False) -> None:
    max_value = max(float(value) for value in values) if len(values) else 0.0
    offset = max_value * 0.02 if max_value else 0.1
    for patch, value in zip(ax.patches, values):
        if percent:
            label = f"{float(value):.1f}%"
        elif abs(float(value)) >= 1000:
            label = f"{float(value):,.0f}"
        else:
            label = f"{float(value):.0f}"
        ax.text(
            patch.get_x() + patch.get_width() / 2,
            patch.get_height() + offset,
            label,
            ha="center",
            va="bottom",
            fontsize=9,
        )


def save_teacher_policy_comparison(pushback_df: pd.DataFrame, out_path: Path) -> None:
    df = _ordered(pushback_df)
    labels = _labels(df)
    colors = _colors(df)
    columns = [
        ("attack_bytes_reaching_victim", "Attack bytes tới victim", "Càng thấp càng tốt"),
        ("benign_bytes_reaching_victim", "Benign bytes giữ lại", "Càng cao càng tốt"),
        ("false_block_events", "Số lần chặn nhầm", "Càng thấp càng tốt"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8))
    for ax, (column, title, subtitle) in zip(axes, columns):
        values = df[column].astype(float).tolist()
        ax.bar(labels, values, color=colors, width=0.65)
        ax.set_title(f"{title}\n{subtitle}", fontsize=11, fontweight="bold")
        ax.tick_params(axis="x", rotation=0)
        ax.ticklabel_format(style="plain", axis="y")
        _apply_axis_style(ax)
        _annotate_bars(ax, values)

    fig.suptitle("So sánh pushback gốc và cải tiến gated", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_attack_timeline(pushback_detail: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.2))
    for policy in POLICY_ORDER:
        subset = (
            pushback_detail[pushback_detail["policy"] == policy]
            .groupby("window", as_index=False)["attack_bytes_reaching_victim"]
            .sum()
        )
        ax.plot(
            subset["window"],
            subset["attack_bytes_reaching_victim"],
            label=POLICY_LABELS.get(policy, policy).replace("\n", " "),
            color=POLICY_COLORS.get(policy, "#4C78A8"),
            linewidth=3 if policy == "gated_pushback" else 2,
        )

    ax.set_title("Attack bytes tới victim theo thời gian", fontsize=13, fontweight="bold")
    ax.set_xlabel("Time window")
    ax.set_ylabel("Attack bytes")
    ax.ticklabel_format(style="plain", axis="y")
    ax.legend()
    _apply_axis_style(ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_improvement_dashboard(pushback_df: pd.DataFrame, comparison_df: pd.DataFrame, out_path: Path) -> None:
    df = _ordered(pushback_df)
    labels = _labels(df)
    colors = _colors(df)

    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5))

    attack_values = df["attack_bytes_reaching_victim"].astype(float).tolist()
    axes[0, 0].bar(labels, attack_values, color=colors, width=0.65)
    axes[0, 0].set_title("Attack bytes tới victim", fontweight="bold")
    axes[0, 0].ticklabel_format(style="plain", axis="y")
    _apply_axis_style(axes[0, 0])
    _annotate_bars(axes[0, 0], attack_values)

    benign_values = df["benign_bytes_reaching_victim"].astype(float).tolist()
    axes[0, 1].bar(labels, benign_values, color=colors, width=0.65)
    axes[0, 1].set_title("Benign bytes được giữ lại", fontweight="bold")
    axes[0, 1].ticklabel_format(style="plain", axis="y")
    _apply_axis_style(axes[0, 1])
    _annotate_bars(axes[0, 1], benign_values)

    false_values = df["false_block_events"].astype(float).tolist()
    axes[1, 0].bar(labels, false_values, color=colors, width=0.65)
    axes[1, 0].set_title("False block events", fontweight="bold")
    _apply_axis_style(axes[1, 0])
    _annotate_bars(axes[1, 0], false_values)

    gated_row = comparison_df[comparison_df["policy"] == "gated_pushback"].iloc[0]
    immediate_row = comparison_df[comparison_df["policy"] == "immediate_pushback"].iloc[0]
    conclusion = (
        "Kết luận chính\n\n"
        "Original/immediate pushback chặn ngay sau 1 lần phát hiện malicious, "
        "nên giảm attack rất mạnh nhưng dễ chặn nhầm benign.\n\n"
        "Gated pushback chỉ chặn sau 2 lần malicious liên tiếp. "
        f"Trong run này, gated vẫn giảm {gated_row['attack_byte_reduction_vs_no_pushback_pct']:.2f}% attack bytes "
        "so với no pushback, đồng thời giữ lại nhiều benign traffic hơn immediate.\n\n"
        f"False block: immediate = {int(immediate_row['false_block_events'])}, "
        f"gated = {int(gated_row['false_block_events'])}."
    )
    axes[1, 1].axis("off")
    axes[1, 1].text(
        0.02,
        0.98,
        conclusion,
        va="top",
        ha="left",
        fontsize=11,
        wrap=True,
        bbox={"boxstyle": "round,pad=0.6", "facecolor": "#F5F7FA", "edgecolor": "#B0BEC5"},
    )

    fig.suptitle("Gated Pushback Improvement Dashboard", fontsize=15, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
