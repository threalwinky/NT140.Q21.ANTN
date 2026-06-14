from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd

IMPROVEMENT_DIR = Path(__file__).resolve().parent
REPRO_ROOT = IMPROVEMENT_DIR.parent
SRC_DIR = REPRO_ROOT / "src"
OUTPUT = IMPROVEMENT_DIR / "output"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from data_pipeline import build_dataset
from model_pipeline import classify_models, train_pushback_model_bundle
from pushback_sim import generate_pushback_trace, simulate_pushback
from report_utils_improvement import (
    save_attack_timeline,
    save_improvement_dashboard,
    save_teacher_policy_comparison,
)

POLICIES = ["no_pushback", "immediate_pushback", "hierarchical_confidence_pushback"]
POLICY_VI = {
    "no_pushback": "Không pushback: baseline, không chặn upstream",
    "immediate_pushback": "Pushback gốc/paper-like: chặn ngay sau 1 lần phát hiện malicious",
    "hierarchical_confidence_pushback": (
        "Cải tiến phân cấp: edge xác nhận sớm, core xác nhận sâu hơn, "
        "sau đó mới leo thang monitor -> rate-limit -> pushback -> block"
    ),
}
TEACHER_NOTES = {
    "no_pushback": "Baseline để đo lượng attack nếu không có cơ chế giảm thiểu.",
    "immediate_pushback": "Giảm attack rất mạnh nhưng dễ chặn nhầm benign khi model false positive.",
    "hierarchical_confidence_pushback": (
        "Cân bằng hơn: hệ thống chỉ hard block khi bằng chứng đủ mạnh, "
        "còn trước đó sẽ đi qua các mức monitor, local rate-limit và upstream pushback."
    ),
}


def _pct_reduction(baseline: float, value: float) -> float:
    return 100.0 * (baseline - value) / max(baseline, 1.0)


def _pct_ratio(value: float, baseline: float) -> float:
    return 100.0 * value / max(baseline, 1.0)


def build_teacher_comparison(pushback_df: pd.DataFrame) -> pd.DataFrame:
    indexed = pushback_df.set_index("policy")
    no_pushback = indexed.loc["no_pushback"]
    immediate = indexed.loc["immediate_pushback"]
    immediate_false_blocks = float(immediate["false_block_events"])

    rows: list[dict[str, Any]] = []
    for policy in POLICIES:
        row = indexed.loc[policy]
        false_blocks = float(row["false_block_events"])
        false_block_reduction = None
        if policy != "no_pushback" and immediate_false_blocks > 0:
            false_block_reduction = _pct_reduction(immediate_false_blocks, false_blocks)

        rows.append(
            {
                "policy": policy,
                "policy_vietnamese": POLICY_VI[policy],
                "attack_bytes_reaching_victim": float(row["attack_bytes_reaching_victim"]),
                "benign_bytes_reaching_victim": float(row["benign_bytes_reaching_victim"]),
                "attack_flows_reaching_victim": int(row["attack_flows_reaching_victim"]),
                "benign_flows_reaching_victim": int(row["benign_flows_reaching_victim"]),
                "false_block_events": int(row["false_block_events"]),
                "total_block_events": int(row["total_block_events"]),
                "monitor_events": int(row.get("monitor_events", 0)),
                "local_rate_limit_events": int(row.get("local_rate_limit_events", 0)),
                "upstream_pushback_events": int(row.get("upstream_pushback_events", 0)),
                "hard_block_events": int(row.get("hard_block_events", 0)),
                "attack_byte_reduction_vs_no_pushback_pct": _pct_reduction(
                    float(no_pushback["attack_bytes_reaching_victim"]),
                    float(row["attack_bytes_reaching_victim"]),
                ),
                "benign_byte_preserved_vs_no_pushback_pct": _pct_ratio(
                    float(row["benign_bytes_reaching_victim"]),
                    float(no_pushback["benign_bytes_reaching_victim"]),
                ),
                "false_block_reduction_vs_immediate_pct": false_block_reduction,
                "teacher_note": TEACHER_NOTES[policy],
            }
        )

    return pd.DataFrame(rows)


def _fmt_float(value: float) -> str:
    return f"{value:,.0f}"


def _fmt_pct(value: float) -> str:
    return f"{value:.2f}%"


def write_teacher_summary(dataset_source: str, comparison_df: pd.DataFrame, output_dir: Path) -> None:
    no_pushback = comparison_df[comparison_df["policy"] == "no_pushback"].iloc[0]
    immediate = comparison_df[comparison_df["policy"] == "immediate_pushback"].iloc[0]
    hierarchical = comparison_df[comparison_df["policy"] == "hierarchical_confidence_pushback"].iloc[0]

    lines = [
        "# Hierarchical Confidence-Aware Pushback",
        "",
        "## Mục tiêu",
        "",
        "Thư mục này tách riêng phần cải tiến `Hierarchical Confidence-Aware Pushback` để so sánh với cơ chế pushback gốc/paper-like trong reproduction.",
        "Tất cả kết quả ở đây được ghi riêng trong `reproduction/improvement/output`, không ghi đè kết quả gốc ở `reproduction/output`.",
        "",
        "## Dataset và model",
        "",
        f"- Dataset source: `{dataset_source}`",
        "- Model mitigation dùng hai tầng DT-CTS: edge detector 3 feature và core detector đầy đủ để xác nhận.",
        "- Trace pushback là mô phỏng flow-level gồm nhiều source theo time window, không phải đo trực tiếp từ mạng thật.",
        "",
        "## Ý nghĩa các policy",
        "",
        "| Policy | Ý nghĩa |",
        "|---|---|",
        "| `no_pushback` | Baseline: không chặn upstream. |",
        "| `immediate_pushback` | Pushback gốc/paper-like: phát hiện malicious một lần là block source. |",
        "| `hierarchical_confidence_pushback` | Cải tiến: edge và core cùng tích lũy suspicion score trước khi leo thang mitigation. |",
        "",
        "## Kết quả chính",
        "",
        "| Metric | No pushback | Immediate/original | Hierarchical improvement |",
        "|---|---:|---:|---:|",
        f"| Attack bytes tới victim | {_fmt_float(no_pushback['attack_bytes_reaching_victim'])} | {_fmt_float(immediate['attack_bytes_reaching_victim'])} | {_fmt_float(hierarchical['attack_bytes_reaching_victim'])} |",
        f"| Benign bytes giữ lại | {_fmt_float(no_pushback['benign_bytes_reaching_victim'])} | {_fmt_float(immediate['benign_bytes_reaching_victim'])} | {_fmt_float(hierarchical['benign_bytes_reaching_victim'])} |",
        f"| False block events | {int(no_pushback['false_block_events'])} | {int(immediate['false_block_events'])} | {int(hierarchical['false_block_events'])} |",
        f"| Attack reduction vs no pushback | {_fmt_pct(no_pushback['attack_byte_reduction_vs_no_pushback_pct'])} | {_fmt_pct(immediate['attack_byte_reduction_vs_no_pushback_pct'])} | {_fmt_pct(hierarchical['attack_byte_reduction_vs_no_pushback_pct'])} |",
        f"| Benign preserved vs no pushback | {_fmt_pct(no_pushback['benign_byte_preserved_vs_no_pushback_pct'])} | {_fmt_pct(immediate['benign_byte_preserved_vs_no_pushback_pct'])} | {_fmt_pct(hierarchical['benign_byte_preserved_vs_no_pushback_pct'])} |",
        "",
        "## Nhận xét để báo cáo",
        "",
        f"- `immediate_pushback` giảm attack mạnh nhất về tốc độ phản ứng nhưng false block cao: `{int(immediate['false_block_events'])}` lần chặn nhầm.",
        f"- `hierarchical_confidence_pushback` vẫn giảm `{_fmt_pct(hierarchical['attack_byte_reduction_vs_no_pushback_pct'])}` attack bytes so với không pushback.",
        f"- So với immediate, hierarchical giảm false block từ `{int(immediate['false_block_events'])}` xuống `{int(hierarchical['false_block_events'])}`.",
        f"- Hierarchical giữ lại `{_fmt_pct(hierarchical['benign_byte_preserved_vs_no_pushback_pct'])}` benign bytes so với baseline, trong khi immediate chỉ giữ `{_fmt_pct(immediate['benign_byte_preserved_vs_no_pushback_pct'])}`.",
        f"- Số lần phản ứng theo mức của hierarchical: local rate-limit = `{int(hierarchical['local_rate_limit_events'])}`, upstream pushback = `{int(hierarchical['upstream_pushback_events'])}`, hard block = `{int(hierarchical['hard_block_events'])}`.",
        "",
        "## File nên mở khi show cho thầy",
        "",
        "1. `hierarchical_improvement_dashboard.png`",
        "2. `teacher_policy_comparison.png`",
        "3. `teacher_attack_timeline.png`",
        "4. `teacher_comparison_table.csv`",
    ]
    (output_dir / "TEACHER_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)

    df, dataset_source = build_dataset()
    (OUTPUT / "improvement_dataset_source.txt").write_text(dataset_source, encoding="utf-8")

    (
        metrics_df,
        threshold_df,
        trained_models,
        _,
        _,
        _,
        _,
        split_metadata,
    ) = classify_models(df)
    metrics_df.to_csv(OUTPUT / "classification_metrics_reference.csv", index=False)
    threshold_df.to_csv(OUTPUT / "threshold_metrics_reference.csv", index=False)

    pushback_model_bundle = train_pushback_model_bundle(
        df,
        train_indices=split_metadata["train_indices"],
        core_model=trained_models["DT-CTS"],
    )

    trace_df = generate_pushback_trace(df)
    policy_rows = []
    detail_frames = []

    for policy in POLICIES:
        detail_df, summary = simulate_pushback(pushback_model_bundle, trace_df, policy)
        detail_frames.append(detail_df)
        policy_rows.append(summary)

    pushback_df = pd.DataFrame(policy_rows)
    pushback_detail = pd.concat(detail_frames, ignore_index=True)
    comparison_df = build_teacher_comparison(pushback_df)

    pushback_df.to_csv(OUTPUT / "improvement_pushback_metrics.csv", index=False)
    pushback_detail.to_csv(OUTPUT / "improvement_pushback_detail.csv", index=False)
    comparison_df.to_csv(OUTPUT / "teacher_comparison_table.csv", index=False)

    save_teacher_policy_comparison(pushback_df, OUTPUT / "teacher_policy_comparison.png")
    save_attack_timeline(pushback_detail, OUTPUT / "teacher_attack_timeline.png")
    save_improvement_dashboard(pushback_df, comparison_df, OUTPUT / "hierarchical_improvement_dashboard.png")
    write_teacher_summary(dataset_source, comparison_df, OUTPUT)

    print("Hierarchical confidence-aware pushback outputs written to:")
    print(OUTPUT)
    print()
    print(comparison_df.to_string(index=False))


if __name__ == "__main__":
    main()
