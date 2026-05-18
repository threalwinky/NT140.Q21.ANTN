from __future__ import annotations

import argparse
import json
import sys
from math import floor
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPRO_SRC = PROJECT_ROOT / "reproduction" / "src"
if str(REPRO_SRC) not in sys.path:
    sys.path.insert(0, str(REPRO_SRC))

from cli_templates import switch_commands
from config import FEATURE_NAMES, KAGGLE_DATASET_SLUG, KAGGLE_WEDNESDAY_PARQUET
from data_pipeline import build_dataset, load_kaggle_wednesday_subset, synthesize_flows
from model_pipeline import load_repo_dt_cts
from tree_to_ternary import tree_to_attack_bin_values

SWITCHES = ("s1", "s2", "s3")


def _p4_threshold(value: float | int) -> int:
    return max(0, floor(float(value)))


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, set):
        return [_jsonable(item) for item in sorted(value)]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    return value


def _load_dataset(dataset: str, seed: int, per_class: int) -> Tuple[pd.DataFrame, str]:
    if dataset == "synthetic":
        return synthesize_flows(seed=seed), "Synthetic DDoS-like flow dataset"
    if dataset == "kaggle":
        return (
            load_kaggle_wednesday_subset(per_class=per_class, seed=seed),
            f"Raw Kaggle parquet {KAGGLE_DATASET_SLUG}/{KAGGLE_WEDNESDAY_PARQUET}",
        )
    return build_dataset(seed=seed)


def _used_thresholds(model: object) -> Dict[str, List[int]]:
    thresholds = {feature: [] for feature in FEATURE_NAMES}
    for feature_idx, values in getattr(model, "feature_thresholds", {}).items():
        feature = FEATURE_NAMES[int(feature_idx)]
        rounded = sorted({_p4_threshold(value) for value in values})
        if len(rounded) > 3:
            raise ValueError(f"Feature {feature} has more than 3 P4 thresholds after conversion")
        thresholds[feature] = rounded
    return thresholds


def _fallback_thresholds(df: pd.DataFrame, feature: str) -> List[int]:
    series = pd.to_numeric(df[feature], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    if series.empty:
        return [0, 0, 0]

    series = series.clip(lower=0)
    candidates = [_p4_threshold(series.quantile(q)) for q in (0.25, 0.5, 0.75)]
    unique = sorted(set(candidates))
    if not unique:
        unique = [0]
    while len(unique) < 3:
        unique.append(unique[-1])
    return unique[:3]


def _complete_thresholds(raw_thresholds: Dict[str, List[int]], df: pd.DataFrame) -> Dict[str, List[int]]:
    completed: Dict[str, List[int]] = {}
    for feature in FEATURE_NAMES:
        values = sorted(set(raw_thresholds.get(feature, [])))
        if len(values) > 3:
            raise ValueError(f"Feature {feature} has more than 3 thresholds")

        for fallback in _fallback_thresholds(df, feature):
            if len(values) >= 3:
                break
            values = sorted(set(values + [fallback]))

        if not values:
            values = [0]
        while len(values) < 3:
            values.append(values[-1])
        completed[feature] = values[:3]
    return completed


def _train_dtcts(df: pd.DataFrame, seed: int, max_depth: int, min_samples_split: int):
    x = df[FEATURE_NAMES].to_numpy(dtype=float)
    y = df["label"].to_numpy(dtype=int)
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=seed,
        stratify=y,
    )

    RepoDTCTS = load_repo_dt_cts()
    model = RepoDTCTS(max_depth=max_depth, min_samples_split=min_samples_split)
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "test_samples": int(len(y_test)),
    }
    return model, metrics


def export_rules(args: argparse.Namespace) -> Dict[str, Any]:
    df, dataset_source = _load_dataset(args.dataset, args.seed, args.per_class)
    model, metrics = _train_dtcts(df, args.seed, args.max_depth, args.min_samples_split)
    raw_thresholds = _used_thresholds(model)
    thresholds = _complete_thresholds(raw_thresholds, df)
    attack_bin_values = tree_to_attack_bin_values(model.tree, thresholds)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for switch_name in SWITCHES:
        commands = switch_commands(switch_name, thresholds, attack_bin_values)
        (args.output_dir / f"{switch_name}_commands.cli").write_text(commands, encoding="utf-8")

    payload = {
        "dataset": {
            "mode": args.dataset,
            "source": dataset_source,
            "rows": int(len(df)),
            "label_counts": {str(key): int(value) for key, value in df["label"].value_counts().sort_index().items()},
        },
        "model": {
            "name": "DT-CTS",
            "max_depth": args.max_depth,
            "min_samples_split": args.min_samples_split,
            "metrics": metrics,
            "tree": _jsonable(model.tree),
        },
        "feature_order": FEATURE_NAMES,
        "raw_thresholds": raw_thresholds,
        "p4_thresholds": thresholds,
        "attack_bin_values": attack_bin_values,
        "attack_bin_values_hex": [f"0x{value:03x}" for value in attack_bin_values],
        "ternary_mask": "0x3ff",
    }

    rules_path = args.output_dir / "dtcts_rules.json"
    rules_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export DT-CTS rules for the SISTAR BMv2 lab")
    parser.add_argument("--dataset", choices=("synthetic", "kaggle", "auto"), default="synthetic")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "SISTAR" / "BMv2" / "generated")
    parser.add_argument("--topology", choices=("lab3",), default="lab3")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--per-class", type=int, default=2500)
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--min-samples-split", type=int, default=20)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = export_rules(args)
    metrics = payload["model"]["metrics"]
    print(f"Dataset: {payload['dataset']['source']}")
    print(f"Rows: {payload['dataset']['rows']}")
    print(f"DT-CTS accuracy: {metrics['accuracy']:.4f}")
    print(f"DT-CTS F1: {metrics['f1']:.4f}")
    print(f"DDoS ternary entries: {len(payload['attack_bin_values'])}")
    print(f"Wrote rules to: {args.output_dir}")


if __name__ == "__main__":
    main()
