import pandas as pd

from config import OUTPUT
from data_pipeline import build_dataset
from model_pipeline import classify_models
from pushback_sim import generate_pushback_trace, simulate_pushback
from report_utils import save_bar_plot, save_pushback_plot, save_threshold_plot, write_summary


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)

    df, dataset_source = build_dataset()
    (OUTPUT / "dataset_source.txt").write_text(dataset_source, encoding="utf-8")
    metrics_df, threshold_df, trained_models = classify_models(df)

    metrics_df.to_csv(OUTPUT / "classification_metrics.csv", index=False)
    threshold_df.to_csv(OUTPUT / "threshold_metrics.csv", index=False)
    df.to_csv(OUTPUT / "dataset_used.csv", index=False)
    old_dataset = OUTPUT / "synthetic_dataset.csv"
    if old_dataset.exists():
        old_dataset.unlink()

    save_bar_plot(metrics_df, "f1", OUTPUT / "classification_f1.png", "F1 comparison")
    save_bar_plot(metrics_df, "accuracy", OUTPUT / "classification_accuracy.png", "Accuracy comparison")
    save_threshold_plot(threshold_df, OUTPUT / "threshold_usage.png")

    trace_df = generate_pushback_trace(df)
    policy_rows = []
    detail_frames = []
    push_model = trained_models["DT-CTS"]

    for policy in ["no_pushback", "immediate_pushback", "gated_pushback"]:
        detail_df, summary = simulate_pushback(push_model, trace_df, policy)
        detail_frames.append(detail_df)
        policy_rows.append(summary)

    pushback_df = pd.DataFrame(policy_rows)
    pushback_detail = pd.concat(detail_frames, ignore_index=True)

    pushback_df.to_csv(OUTPUT / "pushback_metrics.csv", index=False)
    pushback_detail.to_csv(OUTPUT / "pushback_detail.csv", index=False)
    save_pushback_plot(pushback_detail, OUTPUT / "pushback_attack_bytes.png")
    write_summary(metrics_df, threshold_df, pushback_df)

    print("Classification metrics:")
    print(metrics_df.to_string(index=False))
    print()
    print("Threshold metrics:")
    print(threshold_df.to_string(index=False))
    print()
    print("Pushback metrics:")
    print(pushback_df.to_string(index=False))
    print()
    print(f"Wrote outputs to {OUTPUT}")


if __name__ == "__main__":
    main()
