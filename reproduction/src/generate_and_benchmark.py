from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from config import FEATURE_NAMES, OUTPUT
from paper_benchmark_3models import (
    FEATURE_ORDER_7,
    load_dt_cts_class,
    load_cicids2017_from_combine,
    make_medium_models,
    save_accept_deny_plot,
    save_f1_plot,
    save_plot,
)
from benchmark_metrics import aggregate_benchmark_metrics, compute_training_time_summary
from paper_features import select_top_paper_features
try:
    # reuse generator from multi-dataset validation
    from multi_dataset_validation import generate_dataset_variant
except Exception:
    generate_dataset_variant = None


def _sanitize_features(df: pd.DataFrame, feature_names: List[str], caps: Optional[Dict[str, float]] = None, show_progress: bool = False) -> tuple[np.ndarray, Dict[str, float]]:
    """Convert feature columns to finite float arrays and clip extreme values.

    Returns the cleaned matrix plus per-feature upper caps used.
    """
    # operate on a copy of the requested columns
    frame = df[feature_names].copy()

    # optional progress-aware caps calculation for large datasets
    nrows = len(frame)
    for feature in feature_names:
        frame[feature] = pd.to_numeric(frame[feature], errors="coerce")
    frame = frame.replace([np.inf, -np.inf], np.nan)

    if caps is None:
        caps = {}
        # if the dataset is large and show_progress requested, iterate in chunks
        if show_progress and nrows > 50000:
            try:
                from tqdm.auto import tqdm
            except Exception:
                tqdm = None

            chunk_count = 50
            if tqdm is not None:
                iterator = tqdm(range(chunk_count), desc="Estimating feature caps", unit="chunk")
            else:
                iterator = range(chunk_count)

            # approximate caps by sampling equal-sized chunks
            for i in iterator:
                start = int(i * nrows / chunk_count)
                end = int((i + 1) * nrows / chunk_count)
                part = frame.iloc[start:end]
                for feature in feature_names:
                    series = part[feature].dropna()
                    if feature not in caps:
                        caps[feature] = []
                    if not series.empty:
                        caps[feature].append(float(series.quantile(0.999)))

            # reduce lists to robust cap values
            for feature in feature_names:
                vals = caps.get(feature, [])
                if vals:
                    cap = float(np.median(vals))
                    if not np.isfinite(cap) or cap <= 0:
                        cap = float(frame[feature].dropna().max()) if frame[feature].dropna().size > 0 else 1.0
                else:
                    # fallback to full-series compute
                    series = frame[feature].dropna()
                    cap = float(series.quantile(0.999)) if series.size > 0 else 1.0
                caps[feature] = max(cap, 1.0)
        else:
            for feature in feature_names:
                series = frame[feature].dropna()
                if series.empty:
                    caps[feature] = 1.0
                else:
                    cap = float(series.quantile(0.999))
                    if not np.isfinite(cap) or cap <= 0:
                        cap = float(series.max()) if np.isfinite(series.max()) else 1.0
                    caps[feature] = max(cap, 1.0)

    for feature in feature_names:
        frame[feature] = frame[feature].fillna(0.0).clip(lower=0.0, upper=caps.get(feature, 1.0))

    if show_progress and nrows > 50000:
        print(f"Sanitized {nrows} rows × {len(feature_names)} features (caps applied)")

    return frame.to_numpy(dtype=np.float64), caps


def benchmark_feature_sweep(train_df: pd.DataFrame, test_df: pd.DataFrame, sample_limit: Optional[int] = None) -> pd.DataFrame:
    """Generate 3/5/7-feature benchmark results in the same style as the result folder plots."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support
    from sklearn.tree import DecisionTreeClassifier

    rows: List[Dict] = []

    if sample_limit is not None and sample_limit > 0:
        if len(train_df) > sample_limit:
            train_df = train_df.sample(n=sample_limit, random_state=42).reset_index(drop=True)
        if len(test_df) > sample_limit:
            test_df = test_df.sample(n=sample_limit, random_state=42).reset_index(drop=True)

    selected_order = select_top_paper_features(train_df, max_features=7)

    for n_feat in [3, 5, 7]:
        selected = selected_order[: min(n_feat, len(selected_order))]
        if len(selected) < 3:
            raise ValueError("Not enough features for 3/5/7 benchmark plots")

        X_train, caps = _sanitize_features(train_df, selected)
        y_train = train_df["label"].to_numpy(dtype=int)
        X_test, _ = _sanitize_features(test_df, selected, caps=caps)
        y_test = test_df["label"].to_numpy(dtype=int)

        models = make_medium_models()

        def count_sklearn_thresholds(model) -> int:
            return int(np.count_nonzero(model.tree_.feature >= 0))

        def count_rf_thresholds(model) -> int:
            if not getattr(model, "estimators_", None):
                return 0
            return int(sum(np.count_nonzero(estimator.tree_.feature >= 0) for estimator in model.estimators_))

        def count_dtcts_thresholds(model) -> int:
            if hasattr(model, "feature_thresholds") and isinstance(model.feature_thresholds, dict):
                return int(sum(len(values) for values in model.feature_thresholds.values()))

            seen = {}

            def walk(node):
                if not node or "class" in node:
                    return
                seen.setdefault(int(node["feature"]), set()).add(float(node["threshold"]))
                walk(node.get("left"))
                walk(node.get("right"))

            walk(getattr(model, "tree", None))
            return int(sum(len(values) for values in seen.values()))

        for name, model in models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            precision_attack, recall_attack, f1_attack, support_attack = precision_recall_fscore_support(
                y_test, y_pred, labels=[1], zero_division=0
            )
            cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
            tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])

            if name == "DT":
                threshold_count = count_sklearn_thresholds(model)
            elif name == "RF":
                threshold_count = count_rf_thresholds(model)
            else:
                threshold_count = count_dtcts_thresholds(model)

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


def train_models_on_full(df: pd.DataFrame, sample_limit: Optional[int] = None):
    """Train DT, RF, DT-CTS on provided DataFrame. If sample_limit set, sample for smoke tests."""
    try:
        available_features = select_top_paper_features(df, max_features=7)
    except ValueError:
        available_features = [f for f in FEATURE_NAMES if f in df.columns]
    if len(available_features) < 3:
        raise ValueError(f"Not enough features available for training: found {available_features}")

    X, caps = _sanitize_features(df, available_features)
    y = df["label"].to_numpy(dtype=int)

    if sample_limit is not None and sample_limit > 0 and sample_limit < len(y):
        rng = np.random.default_rng(42)
        idx = rng.choice(len(y), size=sample_limit, replace=False)
        X = X[idx]
        y = y[idx]

    models = make_medium_models()

    training_times: Dict[str, float] = {}
    trained: Dict[str, object] = {}

    for name, model in models.items():
        start = time.time()
        n_samples = X.shape[0]
        print(f"Training {name} on {n_samples} samples...")

        # run fit and show periodic elapsed-time updates for long runs
        if n_samples > 100000:
            # spawn fit in background thread and print elapsed time every 5s
            import threading

            def _fit_model():
                model.fit(X, y)

            t = threading.Thread(target=_fit_model, daemon=True)
            t.start()
            elapsed = 0
            while t.is_alive():
                time.sleep(5)
                elapsed += 5
                print(f"  {name} training elapsed {elapsed}s...")
            end = time.time()
        else:
            # small runs: synchronous fit
            model.fit(X, y)
            end = time.time()
        training_times[name] = end - start
        setattr(model, "feature_names", available_features)
        setattr(model, "feature_caps", caps)
        trained[name] = model

    return trained, training_times, available_features, caps


def benchmark_on_variants(trained: Dict[str, object], training_times: Dict[str, float], variants: List[str], sample_limit: Optional[int] = None, feature_list: Optional[List[str]] = None, feature_caps: Optional[Dict[str, float]] = None, cicids2017_test: Optional[pd.DataFrame] = None, data_benchmark_path: Optional[str] = None) -> pd.DataFrame:
    """Benchmark trained models on the provided held-out dataset(s)."""
    results = []

    for variant in variants:
        # use the provided hold-out split when benchmarking the current workflow
        if variant in {"COMBINE_80_20_HOLDOUT", "HOLDOUT_80_20", "COMBINE_75_25_HOLDOUT", "HOLDOUT_75_25"}:
            if cicids2017_test is None:
                raise ValueError(f"Variant {variant} requires cicids2017_test")
            df_test = cicids2017_test
        # support the special synthetic file generated by our random generator
        elif variant == "DATA_BENCHMARK":
            if data_benchmark_path is None:
                data_benchmark_path = str(OUTPUT / "data_benchmark.csv")
            df_test = pd.read_csv(data_benchmark_path)
        elif variant == "CICIDS2017":
            # prefer the provided hold-out test split; otherwise load from combine or synthesize
            if cicids2017_test is not None:
                df_test = cicids2017_test
            else:
                try:
                    df_test = load_cicids2017_from_combine()
                except Exception:
                    if generate_dataset_variant is None:
                        raise RuntimeError("No generator available for synthetic variants")
                    df_test = generate_dataset_variant("CICIDS2017", n_benign=2400, n_attack=2400, seed=42)
        else:
            if generate_dataset_variant is None:
                raise RuntimeError("No generator available for synthetic variants")
            df_test = generate_dataset_variant(variant, n_benign=2400, n_attack=2400, seed=42)

        # optional sample for speed
        if sample_limit is not None and sample_limit > 0 and sample_limit < len(df_test):
            df_test = df_test.sample(n=sample_limit, random_state=42).reset_index(drop=True)

        # ensure we use the same features as training
        if feature_list is None:
            feature_list = [f for f in FEATURE_NAMES if f in df_test.columns]

        missing = [f for f in feature_list if f not in df_test.columns]
        if missing:
            raise ValueError(f"Test variant {variant} missing features required for training: {missing}")

        X_test, _ = _sanitize_features(df_test, feature_list, caps=feature_caps)
        y_test = df_test["label"].to_numpy(dtype=int)

        # predictions per model
        y_pred_dict: Dict[str, np.ndarray] = {}
        for name, model in trained.items():
            y_pred = model.predict(X_test)
            y_pred_dict[name] = y_pred

        bench_df = aggregate_benchmark_metrics(trained, X_test, y_test, y_pred_dict, training_times)
        bench_df["variant"] = variant
        results.append(bench_df)

        # save per-variant csv
        OUTPUT.mkdir(parents=True, exist_ok=True)
        file_name = "traffic_benchmark_data_benchmark.csv" if variant == "DATA_BENCHMARK" else f"traffic_benchmark_{variant}.csv"
        bench_df.to_csv(OUTPUT / file_name, index=False)

    return pd.concat(results, ignore_index=True)


def main(sample_limit: Optional[int] = None):
    """Train on CICIDS2017 extracted from ZIP and benchmark on the 80/20 hold-out split.

    Args:
        sample_limit: optional integer to limit samples for quick testing.
    """
    OUTPUT.mkdir(parents=True, exist_ok=True)

    # Load the same paper-compatible CICIDS2017 view used by
    # paper_benchmark_3models.py so both entrypoints produce comparable CSVs.
    try:
        df_train = load_cicids2017_from_combine()
        print("Loaded training data from CICIDS2017 combine.csv (paper-compatible BENIGN vs Wednesday DoS subset)")
    except Exception:
        raise RuntimeError("Unable to obtain training dataset")

    from sklearn.model_selection import train_test_split

    train_df, test_df = train_test_split(df_train, test_size=0.2, random_state=42, stratify=df_train["label"])
    print(f"Train rows: {len(train_df)}, Benchmark rows: {len(test_df)} (80/20 split)")

    trained, training_times, feature_list, feature_caps = train_models_on_full(train_df, sample_limit=sample_limit)
    times_df = compute_training_time_summary(training_times)
    times_df.to_csv(OUTPUT / "training_times_full.csv", index=False)

    # Benchmark on the 20% hold-out split from combine.csv.
    variants = ["COMBINE_80_20_HOLDOUT"]
    agg = benchmark_on_variants(
        trained,
        training_times,
        variants,
        sample_limit=sample_limit,
        feature_list=feature_list,
        feature_caps=feature_caps,
        cicids2017_test=test_df,
    )
    agg.to_csv(OUTPUT / "traffic_benchmarks_aggregated.csv", index=False)
    paper_style_df = benchmark_feature_sweep(train_df, test_df, sample_limit=sample_limit)
    paper_style_df.to_csv(OUTPUT / "benchmark_cicids2017_dt_rf_dtcts.csv", index=False)
    save_plot(paper_style_df)
    save_f1_plot(paper_style_df)
    save_accept_deny_plot(paper_style_df)

    print("Wrote traffic benchmark CSVs to output/")
    return agg


if __name__ == "__main__":
    main()
