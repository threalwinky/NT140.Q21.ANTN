from __future__ import annotations

import importlib.util
import json
import time
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier as SkDecisionTreeClassifier

from config import FEATURE_NAMES, MODEL_SCALE_MEDIUM, RANDOM_STATE, SISTAR_MODEL, TEST_SIZE
from paper_features import sanitize_feature_matrix, select_top_paper_features


def load_repo_dt_cts():
    spec = importlib.util.spec_from_file_location("sistar_dt_cts", SISTAR_MODEL)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {SISTAR_MODEL}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.DecisionTreeClassifier


def sklearn_tree_thresholds(model, feature_names: List[str]) -> Dict[str, List[float]]:
    tree = model.tree_
    by_feature: Dict[str, List[float]] = {name: [] for name in feature_names}
    for feature_idx, threshold in zip(tree.feature, tree.threshold):
        if 0 <= feature_idx < len(feature_names):
            by_feature[feature_names[feature_idx]].append(float(threshold))
    return {k: sorted(set(v)) for k, v in by_feature.items() if v}


def sklearn_forest_thresholds(model, feature_names: List[str]) -> Dict[str, List[float]]:
    merged: Dict[str, List[float]] = {name: [] for name in feature_names}
    for estimator in model.estimators_:
        tree_thresholds = sklearn_tree_thresholds(estimator, feature_names)
        for feature_name, thresholds in tree_thresholds.items():
            merged[feature_name].extend(thresholds)
    return {k: sorted(set(v)) for k, v in merged.items() if v}


def sklearn_tree_threshold_counts(model, feature_names: List[str]) -> Dict[str, int]:
    counts: Dict[str, int] = {name: 0 for name in feature_names}
    for feature_idx in model.tree_.feature:
        if 0 <= feature_idx < len(feature_names):
            counts[feature_names[feature_idx]] += 1
    return {k: v for k, v in counts.items() if v}


def sklearn_forest_threshold_counts(model, feature_names: List[str]) -> Dict[str, int]:
    counts: Dict[str, int] = {name: 0 for name in feature_names}
    for estimator in model.estimators_:
        for feature_name, count in sklearn_tree_threshold_counts(estimator, feature_names).items():
            counts[feature_name] += count
    return {k: v for k, v in counts.items() if v}


def walk_repo_tree(node, acc: Dict[int, set]):
    if "class" in node:
        return
    acc.setdefault(int(node["feature"]), set()).add(float(node["threshold"]))
    walk_repo_tree(node["left"], acc)
    walk_repo_tree(node["right"], acc)


def repo_dt_cts_thresholds(model, feature_names: List[str]) -> Dict[str, List[float]]:
    acc: Dict[int, set] = {}
    walk_repo_tree(model.tree, acc)
    return {feature_names[idx]: sorted(values) for idx, values in acc.items() if idx < len(feature_names)}


def total_thresholds(threshold_map: Dict[str, List[float]]) -> int:
    return sum(len(v) for v in threshold_map.values())


def make_repo_dtcts(max_depth: int | None = None):
    RepoDTCTS = load_repo_dt_cts()
    return RepoDTCTS(
        max_depth=MODEL_SCALE_MEDIUM["max_depth"] if max_depth is None else max_depth,
        min_samples_split=MODEL_SCALE_MEDIUM["min_samples_split"],
        max_candidate_thresholds=MODEL_SCALE_MEDIUM["dtcts_max_candidate_thresholds"],
        max_thresholds_per_feature=MODEL_SCALE_MEDIUM["dtcts_max_thresholds_per_feature"],
    )


def train_pushback_model_bundle(
    df: pd.DataFrame,
    train_indices: np.ndarray,
    core_model: object | None = None,
) -> Dict[str, object]:
    train_df = df.iloc[train_indices].reset_index(drop=True)
    if core_model is not None and getattr(core_model, "feature_names", None):
        feature_order = list(core_model.feature_names)
    else:
        feature_order = select_top_paper_features(train_df, max_features=7)

    edge_features = feature_order[: min(3, len(feature_order))]
    if len(edge_features) < 3:
        raise ValueError(f"Need at least 3 features for the edge detector, found {edge_features}")

    edge_x, edge_caps = sanitize_feature_matrix(train_df, edge_features)
    y_train = train_df["label"].to_numpy(dtype=int)
    edge_model = make_repo_dtcts(max_depth=4)
    edge_model.fit(edge_x, y_train)
    setattr(edge_model, "feature_names", edge_features)
    setattr(edge_model, "feature_caps", edge_caps)

    if core_model is None:
        core_x, core_caps = sanitize_feature_matrix(train_df, feature_order)
        core_model = make_repo_dtcts()
        core_model.fit(core_x, y_train)
        setattr(core_model, "feature_names", feature_order)
        setattr(core_model, "feature_caps", core_caps)

    benign_df = train_df[train_df["label"] == 0]
    if benign_df.empty:
        benign_df = train_df

    profile = {
        "pps_high": float(pd.to_numeric(benign_df["flow_packets_persecond"], errors="coerce").quantile(0.995))
        if "flow_packets_persecond" in benign_df.columns
        else 0.0,
        "small_packet_threshold": float(pd.to_numeric(benign_df["packet_length_mean"], errors="coerce").quantile(0.10))
        if "packet_length_mean" in benign_df.columns
        else 0.0,
    }

    return {
        "edge": edge_model,
        "core": core_model,
        "feature_order": feature_order,
        "profile": profile,
    }


def classify_models(
    df: pd.DataFrame,
) -> Tuple[
    pd.DataFrame,
    pd.DataFrame,
    Dict[str, object],
    np.ndarray,
    np.ndarray,
    Dict[str, float],
    Dict[str, np.ndarray],
    Dict[str, object],
]:
    try:
        available_features = select_top_paper_features(df, max_features=7)
    except ValueError:
        available_features = [feature for feature in FEATURE_NAMES if feature in df.columns]
    if len(available_features) < 3:
        raise ValueError(f"Need at least 3 usable features, found {available_features}")

    X, feature_caps = sanitize_feature_matrix(df, available_features)
    y = df["label"].to_numpy(dtype=int)
    indices = np.arange(len(df))

    train_indices, test_indices = train_test_split(
        indices,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    X_train, X_test = X[train_indices], X[test_indices]
    y_train, y_test = y[train_indices], y[test_indices]

    models = {
        "DT": SkDecisionTreeClassifier(
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
        "DT-CTS": make_repo_dtcts(),
    }

    metrics_rows = []
    threshold_rows = []
    trained = {}
    training_times = {}
    y_pred_dict = {}

    for name, model in models.items():
        start_time = time.time()
        model.fit(X_train, y_train)
        end_time = time.time()
        training_times[name] = end_time - start_time
        setattr(model, "feature_names", available_features)
        setattr(model, "feature_caps", feature_caps)

        y_pred = model.predict(X_test)
        y_pred_dict[name] = y_pred

        metrics_rows.append(
            {
                "model": name,
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, zero_division=0),
                "recall": recall_score(y_test, y_pred, zero_division=0),
                "f1": f1_score(y_test, y_pred, zero_division=0),
            }
        )

        if name == "DT":
            threshold_counts = sklearn_tree_threshold_counts(model, available_features)
        elif name == "RF":
            threshold_counts = sklearn_forest_threshold_counts(model, available_features)
        else:
            threshold_counts = {feature: len(values) for feature, values in repo_dt_cts_thresholds(model, available_features).items()}

        threshold_rows.append(
            {
                "model": name,
                "total_thresholds": sum(threshold_counts.values()),
                "features_used": len(threshold_counts),
                "max_thresholds_on_single_feature": max(threshold_counts.values(), default=0),
                "thresholds_per_feature": json.dumps(threshold_counts),
            }
        )
        trained[name] = model

    split_metadata = {
        "train_indices": train_indices,
        "test_indices": test_indices,
        "feature_names": available_features,
        "feature_caps": feature_caps,
    }

    return (
        pd.DataFrame(metrics_rows),
        pd.DataFrame(threshold_rows),
        trained,
        X_test,
        y_test,
        training_times,
        y_pred_dict,
        split_metadata,
    )
