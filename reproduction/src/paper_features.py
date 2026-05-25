from __future__ import annotations

from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from config import MODEL_SCALE_MEDIUM, PAPER_FEATURE_CANDIDATES, PAPER_REQUIRED_FEATURES, RANDOM_STATE


def available_paper_features(frame: pd.DataFrame, candidates: Sequence[str] | None = None) -> List[str]:
    feature_candidates = list(candidates or PAPER_FEATURE_CANDIDATES)
    return [feature for feature in feature_candidates if feature in frame.columns]


def feature_caps(frame: pd.DataFrame, feature_names: Sequence[str]) -> Dict[str, float]:
    caps: Dict[str, float] = {}
    for feature in feature_names:
        series = pd.to_numeric(frame[feature], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
        if series.empty:
            caps[feature] = 1.0
            continue
        cap = float(series.quantile(0.999))
        if not np.isfinite(cap) or cap <= 0:
            cap = float(series.max()) if np.isfinite(series.max()) else 1.0
        caps[feature] = max(cap, 1.0)
    return caps


def sanitize_feature_frame(
    frame: pd.DataFrame,
    feature_names: Sequence[str],
    caps: Dict[str, float] | None = None,
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    clean = frame[list(feature_names)].copy()
    for feature in feature_names:
        clean[feature] = pd.to_numeric(clean[feature], errors="coerce")
    clean = clean.replace([np.inf, -np.inf], np.nan)

    fitted_caps = feature_caps(clean, feature_names) if caps is None else dict(caps)
    for feature in feature_names:
        clean[feature] = clean[feature].fillna(0.0).clip(lower=0.0, upper=fitted_caps.get(feature, 1.0))
    return clean, fitted_caps


def sanitize_feature_matrix(
    frame: pd.DataFrame,
    feature_names: Sequence[str],
    caps: Dict[str, float] | None = None,
) -> Tuple[np.ndarray, Dict[str, float]]:
    clean, fitted_caps = sanitize_feature_frame(frame, feature_names, caps=caps)
    return clean.to_numpy(dtype=np.float64), fitted_caps


def _representative_sample(
    frame: pd.DataFrame,
    sample_size: int,
    random_state: int,
) -> pd.DataFrame:
    if sample_size <= 0 or len(frame) <= sample_size:
        return frame
    return frame.sample(n=sample_size, random_state=random_state).reset_index(drop=True)


def select_top_paper_features(
    train_df: pd.DataFrame,
    max_features: int = 7,
    candidates: Sequence[str] | None = None,
    sample_size: int = 200_000,
    random_state: int = RANDOM_STATE,
) -> List[str]:
    available = available_paper_features(train_df, candidates)
    if len(available) < 3:
        raise ValueError(f"Need at least 3 paper-style features, found {available}")

    selector_df = _representative_sample(train_df, sample_size=sample_size, random_state=random_state)
    x, _ = sanitize_feature_matrix(selector_df, available)
    y = selector_df["label"].to_numpy(dtype=int)

    selector = RandomForestClassifier(
        n_estimators=MODEL_SCALE_MEDIUM["n_estimators"],
        max_depth=MODEL_SCALE_MEDIUM["max_depth"],
        min_samples_split=MODEL_SCALE_MEDIUM["min_samples_split"],
        random_state=random_state,
        n_jobs=-1,
    )
    selector.fit(x, y)
    ranked = sorted(zip(available, selector.feature_importances_), key=lambda item: item[1], reverse=True)
    ordered: List[str] = []
    for feature in PAPER_REQUIRED_FEATURES:
        if feature in available and feature not in ordered:
            ordered.append(feature)
    for feature, _ in ranked:
        if feature not in ordered:
            ordered.append(feature)
    return ordered[: min(max_features, len(ordered))]


def describe_feature_order(feature_order: Iterable[str]) -> str:
    return ",".join(feature_order)
