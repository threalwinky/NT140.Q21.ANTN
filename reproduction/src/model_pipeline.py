from __future__ import annotations

import importlib.util
import json
from typing import Dict, List, Tuple

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier as SkDecisionTreeClassifier

from config import FEATURE_NAMES, SISTAR_MODEL


def load_repo_dt_cts():
    spec = importlib.util.spec_from_file_location("sistar_dt_cts", SISTAR_MODEL)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {SISTAR_MODEL}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.DecisionTreeClassifier


def sklearn_tree_thresholds(model) -> Dict[str, List[float]]:
    tree = model.tree_
    by_feature: Dict[str, List[float]] = {name: [] for name in FEATURE_NAMES}
    for feature_idx, threshold in zip(tree.feature, tree.threshold):
        if feature_idx >= 0:
            by_feature[FEATURE_NAMES[feature_idx]].append(float(threshold))
    return {k: sorted(set(v)) for k, v in by_feature.items() if v}


def sklearn_forest_thresholds(model) -> Dict[str, List[float]]:
    merged: Dict[str, List[float]] = {name: [] for name in FEATURE_NAMES}
    for estimator in model.estimators_:
        tree_thresholds = sklearn_tree_thresholds(estimator)
        for feature_name, thresholds in tree_thresholds.items():
            merged[feature_name].extend(thresholds)
    return {k: sorted(set(v)) for k, v in merged.items() if v}


def walk_repo_tree(node, acc: Dict[int, set]):
    if "class" in node:
        return
    acc.setdefault(int(node["feature"]), set()).add(float(node["threshold"]))
    walk_repo_tree(node["left"], acc)
    walk_repo_tree(node["right"], acc)


def repo_dt_cts_thresholds(model) -> Dict[str, List[float]]:
    acc: Dict[int, set] = {}
    walk_repo_tree(model.tree, acc)
    return {FEATURE_NAMES[idx]: sorted(values) for idx, values in acc.items()}


def total_thresholds(threshold_map: Dict[str, List[float]]) -> int:
    return sum(len(v) for v in threshold_map.values())


def classify_models(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, object]]:
    X = df[FEATURE_NAMES].to_numpy(dtype=float)
    y = df["label"].to_numpy(dtype=int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    RepoDTCTS = load_repo_dt_cts()

    models = {
        "DT": SkDecisionTreeClassifier(max_depth=6, min_samples_split=20, random_state=42),
        "RF": RandomForestClassifier(n_estimators=9, max_depth=6, min_samples_split=20, random_state=42),
        "DT-CTS": RepoDTCTS(max_depth=6, min_samples_split=20),
    }

    metrics_rows = []
    threshold_rows = []
    trained = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
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
            thresholds = sklearn_tree_thresholds(model)
        elif name == "RF":
            thresholds = sklearn_forest_thresholds(model)
        else:
            thresholds = repo_dt_cts_thresholds(model)

        threshold_rows.append(
            {
                "model": name,
                "total_thresholds": total_thresholds(thresholds),
                "features_used": len(thresholds),
                "max_thresholds_on_single_feature": max((len(v) for v in thresholds.values()), default=0),
                "thresholds_per_feature": json.dumps({k: len(v) for k, v in thresholds.items()}),
            }
        )
        trained[name] = model

    return pd.DataFrame(metrics_rows), pd.DataFrame(threshold_rows), trained
